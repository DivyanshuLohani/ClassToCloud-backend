import os
import boto3
from django.conf import settings
from ffmpeg import input as ffmpeg_input, output as ffmpeg_output, run as ffmpeg_run

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL if settings.DEBUG else None,
)
bucket_name = settings.AWS_STORAGE_BUCKET_NAME


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
            "preset": "fast",
            "crf": 30,
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


def transcode_and_upload_dash(resolution, input_url, output_dir, lecture_id):
    resolution_value = resolution["resolution"]
    video_bitrate = resolution["video_bitrate"]
    audio_bitrate = resolution["audio_bitrate"]
    output_filename = f"{resolution_value}.mpd"  # DASH uses .mpd file
    output_path = os.path.join(output_dir, output_filename)
    segment_path = os.path.join(
        output_dir, f"{resolution_value}_%03d.m4s")  # .m4s segments for DASH

    # Transcoding with ffmpeg to create DASH segments
    ffmpeg_in = ffmpeg_input(input_url)
    ffmpeg_out = ffmpeg_output(
        ffmpeg_in,
        segment_path,
        output_path,
        **{
            "c:v": "libx264",
            "b:v": video_bitrate,
            "c:a": "aac",
            "b:a": audio_bitrate,
            "vf": f"scale={resolution_value}",
            "f": "dash",  # Set the format to DASH
            "dash_segment_filename": segment_path,  # Specify segment filename pattern
            "map": "0",  # Maps all streams (video and audio)
        }
    )
    ffmpeg_run(ffmpeg_out)

    # Upload transcoded files (MPD and .m4s segments)
    for root, _, files in os.walk(output_dir):
        for file_name in files:
            if file_name.startswith(resolution_value):
                file_path = os.path.join(root, file_name)
                s3_key = f"lectures/{lecture_id}/{file_name}"
                with open(file_path, "rb") as f:
                    s3.upload_fileobj(f, bucket_name, s3_key)

    return output_filename


def create_dash_master_playlist(output_dir, lecture_id, resolution_configs):
    # The master playlist is the MPD file itself in DASH
    master_mpd_path = os.path.join(output_dir, "master.mpd")

    # Create an MPD (Media Presentation Description) file manually or with a library
    # This part would generally need to define the representations for each transcoded version.

    # Example of building the MPD (simplified)
    mpd_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    mpd_content += '<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static" mediaPresentationDuration="PT0H10M0S" profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">\n'

    # Add representation information for each resolution/variant
    for res_config in resolution_configs:
        resolution_value = res_config["resolution"]
        video_bitrate = res_config["video_bitrate"]
        audio_bitrate = res_config["audio_bitrate"]

        # The segment URL will be relative or absolute depending on your setup
        video_segment_url = f"lectures/{
            lecture_id}/{resolution_value}_%03d.m4s"
        audio_segment_url = f"lectures/{lecture_id}/{
            resolution_value}_audio_%03d.m4s"

        mpd_content += f'  <AdaptationSet mimeType="video/mp4" codecs="avc1.640028" width="{resolution_value.split(
            "x")[0]}" height="{resolution_value.split("x")[1]}" frameRate="25" segmentAlignment="true">\n'
        mpd_content += f'    <Representation bandwidth="{video_bitrate}" width="{resolution_value.split(
            "x")[0]}" height="{resolution_value.split("x")[1]}" codecs="avc1.640028" frameRate="25">\n'
        mpd_content += f'      <BaseURL>{video_segment_url}</BaseURL>\n'
        mpd_content += '      <SegmentList timescale="1000" duration="10000" startNumber="1">\n'
        mpd_content += '        <SegmentURL media="video_segment" indexRange="0-1000"/>\n'
        mpd_content += '      </SegmentList>\n'
        mpd_content += '    </Representation>\n'

        # Add audio representation
        mpd_content += f'  <AdaptationSet mimeType="audio/mp4" codecs="mp4a.40.2" lang="en" segmentAlignment="true">\n'
        mpd_content += f'    <Representation bandwidth="{
            audio_bitrate}" codecs="mp4a.40.2">\n'
        mpd_content += f'      <BaseURL>{audio_segment_url}</BaseURL>\n'
        mpd_content += '      <SegmentList timescale="1000" duration="10000" startNumber="1">\n'
        mpd_content += '        <SegmentURL media="audio_segment" indexRange="0-1000"/>\n'
        mpd_content += '      </SegmentList>\n'
        mpd_content += '    </Representation>\n'

    # Close the MPD content
    mpd_content += '</MPD>\n'
