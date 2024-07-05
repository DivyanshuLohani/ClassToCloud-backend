from celery import shared_task
import subprocess
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from django.conf import settings
from .models import Lecture, GoogleCredentials
import json

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

    input_path = lecture.file.path
    output_dir = f'uploads/lectures/{lecture_id}'
    os.makedirs(output_dir, exist_ok=True)
    variant_playlists = []

    for i, res in enumerate(resolutions):
        resolution = res['resolution']
        video_bitrate = res['video_bitrate']
        audio_bitrate = res['audio_bitrate']
        output_filename = f"{resolution}.m3u8"
        output_path = f'{output_dir}/{output_filename}'
        segment_path = f'{output_dir}/{resolution}_%03d.ts'

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
            lecture.save()
        except subprocess.CalledProcessError:
            lecture.status = 'failed'
            lecture.save()
            return

        variant_playlists.append({
            'resolution': resolution,
            'output_file_name': output_filename,
        })

    master_playlist_content = "#EXTM3U\n"
    for variant in variant_playlists:
        resolution = variant['resolution']
        output_file_name = variant['output_file_name']
        bandwidth = 676800 if resolution == '320x180' else 1353600 if resolution == '854x480' else 3230400

        master_playlist_content = master_playlist_content + \
            f"""#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={
                resolution}\n{output_file_name}\n"""

    master_playlist_file_path = f"{output_dir}/master.m3u8"
    with open(master_playlist_file_path, 'w') as f:
        f.write(master_playlist_content)

    lecture.file = master_playlist_file_path
    lecture.save()
    os.remove(input_path)


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
