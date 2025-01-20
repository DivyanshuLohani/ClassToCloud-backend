from .models import Lecture
from core.permissions import OnlyTeacherUpdate, IsTeacher
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import LectureSerializer, CreateLectureSerializer, UploadInitalizerSerializer, UploadChunkSerializer
from .tasks import transcode_video, upload_to_youtube
from django.conf import settings
import boto3
import zlib


s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL if settings.DEBUG else None,
)

LECTURE_FILE_UPLOAD_KEY = "uploads/lectures/{0}"


class LectureUploadInitializeView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs):
        serializer = UploadInitalizerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lecture = Lecture.objects.create(
            chapter=serializer.validated_data['chapter'],
            title=serializer.validated_data['title'],
            type=self.request.user.institute.upload_type
        )

        if not self.request.user.institute == lecture.chapter.subject.batch.institute:
            lecture.delete()
            raise NotFound("Chapter not found.")

        response = s3_client.create_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=LECTURE_FILE_UPLOAD_KEY.format(lecture.uid),
        )

        return Response({"upload_id": response["UploadId"], "uid": lecture.uid}, status=200)


class LectureUploadChunkView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs):
        serializer = UploadChunkSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data['file']
        # crc32_checksum = calculate_crc32(file_obj)
        try:

            response = s3_client.upload_part(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=LECTURE_FILE_UPLOAD_KEY.format(
                    serializer.validated_data['uid']),
                PartNumber=serializer.validated_data['part_number'],
                UploadId=serializer.validated_data['upload_id'],
                Body=file_obj,
            )
            return Response(
                {
                    "status": "success",
                    "uid": serializer.validated_data['uid'],
                    "ETag": response["ETag"]
                }, status=200)

        except Exception as e:
            print(e)
            return Response(
                {
                    "status": "error",
                    "error": "Failed to upload part",
                }, status=500)


class LectureUploadCompleteView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, *args, **kwargs):
        uid = request.data['uid']
        if not uid:
            raise NotFound("Lecture not found.")
        upload_id = request.data['upload_id']
        lecture = Lecture.objects.get(uid=uid)
        if not lecture.chapter.subject.batch.institute == self.request.user.institute:
            raise PermissionDenied(
                "You do not have permission to access this lecture."
            )
        key = LECTURE_FILE_UPLOAD_KEY.format(uid)

        response = s3_client.list_parts(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            UploadId=upload_id,
        )

        parts = [
            {"PartNumber": part['PartNumber'], "ETag": part['ETag'],
                "ChecksumCRC32": part['ChecksumCRC32']}
            for part in response.get('Parts', [])
        ]
        if not parts:
            raise NotFound("Parts not found or have currpted.")

        response = s3_client.complete_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )

        lecture.file = key
        lecture.status = "pending"
        lecture.save()
        if lecture.type == "native":
            transcode_video.delay(lecture.uid)
        else:
            upload_to_youtube.delay(lecture.uid)
        serializer = LectureSerializer(lecture)
        return Response(serializer.data, status=200)


class LectureView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LectureSerializer
    permission_classes = [OnlyTeacherUpdate]
    queryset = Lecture.objects.all()

    def get_object(self):
        c_uid = self.kwargs['c_uid']
        lecture = generics.get_object_or_404(self.get_queryset(), uid=c_uid)

        if (lecture is None) or lecture.chapter.subject.batch.institute != self.request.user.institute:
            raise NotFound()

        return lecture
