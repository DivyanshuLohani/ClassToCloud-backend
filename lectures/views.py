from rest_framework import viewsets
# from chunked_upload.views import ChunkedUploadView, ChunkedUploadCompleteView
from .models import Lecture
from .serializers import LectureSerializer
from .tasks import transcode_video, upload_to_youtube
from rest_framework.exceptions import NotFound, PermissionDenied


class LectureViewSet(viewsets.ModelViewSet):

    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer

    def perform_create(self, serializer):
        lecture = serializer.save()
        if not self.request.user.is_teacher:
            raise PermissionDenied()
        if not self.request.user.institute == lecture.chapter.subject.batch.institute:
            lecture.delete()
            raise NotFound("Chapter not found.")

        # TODO: make it so that server decides wheather video is native or youtube
        # if self.user.institute.type =
        if lecture.type == 'native' and lecture.file:
            lecture.status = 'pending'
            lecture.save()
            transcode_video.delay(lecture.uid)
        elif lecture.type == 'youtube' and lecture.file:
            lecture.status = 'pending'
            lecture.save()
            upload_to_youtube.delay(lecture.uid)

# class VideoChunkedUploadView(ChunkedUploadView):
#     model = VideoChunkedUpload
#     field_name = 'file'


# class VideoChunkedUploadCompleteView(ChunkedUploadCompleteView):
#     model = VideoChunkedUpload

#     def on_completion(self, uploaded_file, request):
#         lecture_id = request.data.get('lecture_id')
#         lecture = Lecture.objects.get(id=lecture_id)
#         lecture.file = uploaded_file
#         lecture.status = 'pending'
#         lecture.save()
#         transcode_video.delay(lecture.id)

#     def get_response_data(self, chunked_upload, request):
#         return {'message': 'Upload complete'}
