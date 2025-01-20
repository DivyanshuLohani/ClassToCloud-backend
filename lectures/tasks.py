from tempfile import TemporaryDirectory, NamedTemporaryFile
from celery import shared_task
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from django.conf import settings
from .models import Lecture, GoogleCredentials
import json
import boto3
from ffmpeg import input as ffmpeg_input, output as ffmpeg_output, run as ffmpeg_run
from django.core.files.storage import default_storage

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL if settings.DEBUG else None,
)
bucket_name = settings.AWS_STORAGE_BUCKET_NAME

# Video resolutions and settings
resolutions = [
    {"resolution": "320x180", "video_bitrate": "500k", "audio_bitrate": "128k"},
    {"resolution": "854x480", "video_bitrate": "1000k", "audio_bitrate": "128k"},
    {"resolution": "1920x1080", "video_bitrate": "3000k", "audio_bitrate": "192k"},
]


@shared_task
def transcode_video(lecture_id):
    lecture = Lecture.objects.get(uid=lecture_id)
    lecture.status = "in_progress"
    lecture.save()

    input_key = lecture.file.name  # S3 key of the uploaded file
    # input_url = f"{settings.AWS_S3_ENDPOINT_URL}/{bucket_name}/{input_key}"
    input_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": input_key}
    )

    # Temporary directory for intermediate files
    with TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, f"lectures/{lecture_id}")
        os.makedirs(output_dir, exist_ok=True)

        # Transcode and upload concurrently
        variant_playlists = []
        with ThreadPoolExecutor(max_workers=len(resolutions)) as executor:
            future_to_resolution = {
                executor.submit(
                    transcode_and_upload, res, input_url, output_dir, lecture_id
                ): res
                for res in resolutions
            }

            for future in as_completed(future_to_resolution):
                resolution = future_to_resolution[future]
                try:
                    output_filename = future.result()
                    variant_playlists.append({
                        "resolution": resolution["resolution"],
                        "output_file_name": output_filename,
                    })
                except Exception as e:
                    lecture.status = "failed"
                    lecture.save()
                    raise e

        # Create master playlist after all transcoding is done
        master_playlist_file_path = os.path.join(output_dir, "master.m3u8")
        create_master_playlist(master_playlist_file_path, variant_playlists)

        # Upload master playlist
        with open(master_playlist_file_path, "rb") as f:
            s3.upload_fileobj(
                f, bucket_name, f"lectures/{lecture_id}/master.m3u8"
            )

        # Delete the object after complete transcoding
        s3.delete_object(Bucket=bucket_name, Key=input_key)

        # Update lecture file to point to the master playlist
        lecture.file = f"lectures/{lecture_id}/master.m3u8"
        lecture.status = "completed"
        lecture.save()


def transcode_and_upload(resolution, input_url, output_dir, lecture_id):
    resolution_value = resolution["resolution"]
    video_bitrate = resolution["video_bitrate"]
    audio_bitrate = resolution["audio_bitrate"]
    output_filename = f"{resolution_value}.m3u8"
    output_path = os.path.join(output_dir, output_filename)
    segment_path = os.path.join(output_dir, f"{resolution_value}_%03d.ts")

    # Transcoding with python-ffmpeg
    ffmpeg_in = ffmpeg_input(input_url)
    ffmpeg_out = ffmpeg_output(
        ffmpeg_in,
        output_path,
        **{
            "c:v": "h264",
            "b:v": video_bitrate,
            "c:a": "aac",
            "b:a": audio_bitrate,
            "vf": f"scale={resolution_value}",
            "f": "hls",
            "hls_time": 10,
            "hls_list_size": 0,
            "hls_segment_filename": segment_path,
        },
    )
    ffmpeg_run(ffmpeg_out)

    # Upload transcoded files
    for root, _, files in os.walk(output_dir):
        for file_name in files:
            if file_name.startswith(resolution_value):
                file_path = os.path.join(root, file_name)
                s3_key = f"lectures/{lecture_id}/{file_name}"
                with open(file_path, "rb") as f:
                    s3.upload_fileobj(f, bucket_name, s3_key)

    return output_filename


def create_master_playlist(master_playlist_file_path, variant_playlists):
    bandwidth_map = {
        "320x180": 676800,
        "854x480": 1353600,
        "1920x1080": 3230400,
    }

    master_playlist_content = "#EXTM3U\n"
    for variant in variant_playlists:
        resolution = variant["resolution"]
        output_file_name = variant["output_file_name"]
        bandwidth = bandwidth_map[resolution]
        master_playlist_content += (
            f"#EXT-X-STREAM-INF:BANDWIDTH={
                bandwidth},RESOLUTION={resolution}\n"
            f"{output_file_name}\n"
        )

    with open(master_playlist_file_path, "w") as f:
        f.write(master_playlist_content)


@shared_task
def upload_to_youtube(lecture_id):
    lecture = Lecture.objects.get(uid=lecture_id)
    lecture.status = "in_progress"
    lecture.save()

    # Handle file from Django storages
    video_file = lecture.file.name
    with default_storage.open(video_file, "rb") as file:
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(file.read())
        temp_file.flush()

    # Disable https requirement for local testing
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    user_cred = GoogleCredentials.objects.first()
    if not user_cred:
        return

    credentials = Credentials.from_authorized_user_info(
        json.loads(user_cred.credentials)
    )

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials
    )

    # Upload video
    request_body = {
        "snippet": {
            "title": lecture.title,
            "description": "Lecture video",
            "tags": ["lecture", "education"],
            "categoryId": "27"  # Education category
        },
        "status": {
            "privacyStatus": "unlisted"  # Change as per your requirement
        }
    }

    media_file = googleapiclient.http.MediaFileUpload(
        temp_file.name, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = request.execute()

    # Save YouTube video ID to the Lecture model
    lecture.video_id = response["id"]
    lecture.status = "completed"
    lecture.file = None
    lecture.save()

    # Clean up the temporary file
    os.remove(temp_file.name)
