from tempfile import NamedTemporaryFile
from celery import shared_task
import subprocess
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from django.conf import settings
from .models import Lecture, GoogleCredentials
import json
import boto3

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL  # LocalStack endpoint or AWS endpoint
)
bucket_name = settings.AWS_STORAGE_BUCKET_NAME

resolutions = [
    {
        'resolution': '320x180',
        'video_bitrate': '500k',
        'audio_bitrate': '64k'
    },
    {
        'resolution': '854x480',
        'video_bitrate': '1000k',
        'audio_bitrate': '128k'
    },
    {
        'resolution': '1280x720',
        'video_bitrate': '2500k',
        'audio_bitrate': '192k'
    }
]


@shared_task
def transcode_video(lecture_id):
    lecture = Lecture.objects.get(uid=lecture_id)
    lecture.status = 'in_progress'
    lecture.save()

    input_key = lecture.file.name  # S3 key of the uploaded file

    # Download the file from S3
    with NamedTemporaryFile(delete=False) as temp_file:
        s3.download_fileobj(bucket_name, input_key, temp_file)
        temp_file.flush()
        input_path = temp_file.name  # Local path of the downloaded file

    # Prepare output directory
    output_dir = os.path.join("/tmp", f"lectures/{lecture_id}")
    os.makedirs(output_dir, exist_ok=True)
    variant_playlists = []

    # Video transcoding logic
    resolutions = [
        {'resolution': '320x180', 'video_bitrate': '500k', 'audio_bitrate': '128k'},
        {'resolution': '854x480', 'video_bitrate': '1000k', 'audio_bitrate': '128k'},
        {'resolution': '1920x1080', 'video_bitrate': '3000k', 'audio_bitrate': '192k'},
    ]

    for _, res in enumerate(resolutions):
        resolution = res['resolution']
        video_bitrate = res['video_bitrate']
        audio_bitrate = res['audio_bitrate']
        output_filename = f"{resolution}.m3u8"
        output_path = os.path.join(output_dir, output_filename)
        segment_path = os.path.join(output_dir, f"{resolution}_%03d.ts")

        command = [
            'ffmpeg',
            '-i', input_path,                       # Input File
            '-c:v', 'h264',                         # Video Codec
            '-b:v', video_bitrate,                  # Video Bitrate
            '-c:a', 'aac',                          # Audio Codec
            '-b:a', audio_bitrate,                  # Audio Bitrate
            '-vf', f'scale={resolution}',           # Video Resolution
            '-f', 'hls',                            # Video Format
            '-hls_time', '10',                      # Video Chunk TIME
            '-hls_list_size', '0',                  # HLS LIST SIZE
            '-hls_segment_filename', segment_path,  # Segment File name
            output_path                             # Output m3u8 File
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            lecture.status = 'failed'
            lecture.save()
            os.remove(input_path)
            return

        variant_playlists.append({
            'resolution': resolution,
            'output_file_name': output_filename,
        })

    # Create master playlist
    master_playlist_content = "#EXTM3U\n"
    for variant in variant_playlists:
        resolution = variant['resolution']
        output_file_name = variant['output_file_name']
        bandwidth = 676800 if resolution == '320x180' else 1353600 if resolution == '854x480' else 3230400

        master_playlist_content += f"#EXT-X-STREAM-INF:BANDWIDTH={
            bandwidth},RESOLUTION={resolution}\n{output_file_name}\n"

    master_playlist_file_path = os.path.join(output_dir, "master.m3u8")
    with open(master_playlist_file_path, 'w') as f:
        f.write(master_playlist_content)

    # Upload transcoded files back to S3
    for root, _, files in os.walk(output_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            s3_key = f"lectures/{lecture_id}/{file_name}"
            with open(file_path, "rb") as f:
                s3.upload_fileobj(f, bucket_name, s3_key)

    # Update lecture with the master playlist path
    lecture.file = f"lectures/{lecture_id}/master.m3u8"
    lecture.status = "completed"
    lecture.save()

    # Clean up local files
    os.remove(input_path)
    for root, _, files in os.walk(output_dir):
        for file_name in files:
            os.remove(os.path.join(root, file_name))
    os.rmdir(output_dir)


@shared_task
def upload_to_youtube(lecture_id):

    lecture = Lecture.objects.get(uid=lecture_id)
    lecture.status = "in_progress"
    lecture.save()

    video_file = lecture.file.path

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
        video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = request.execute()

    # Save YouTube video ID to the Lecture model
    lecture.video_id = response["id"]
    lecture.status = "completed"
    os.remove(lecture.file.path)
    lecture.file = None
    lecture.save()
