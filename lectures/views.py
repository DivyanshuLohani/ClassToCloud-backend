from .models import Lecture
from core.permissions import OnlyTeacherUpdate, IsTeacher
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import generics
from .serializers import LectureSerializer
from .tasks import transcode_video, upload_to_youtube
import subprocess


def get_video_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


class LectureCreateView(generics.CreateAPIView):

    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [IsTeacher]

    def perform_create(self, serializer):
        lecture = serializer.save(type=self.request.user.institute.upload_type)
        lecture.duration = int(get_video_length(lecture.file.path))

        if not self.request.user.institute == lecture.chapter.subject.batch.institute:
            lecture.delete()
            raise NotFound("Chapter not found.")

        if lecture.type == 'native' and lecture.file:
            lecture.status = 'pending'
            lecture.save()
            transcode_video.delay(lecture.uid)
        elif lecture.type == 'youtube' and lecture.file:
            lecture.status = 'pending'
            lecture.save()
            upload_to_youtube.delay(lecture.uid)


class LectureView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LectureSerializer
    permission_classes = [OnlyTeacherUpdate]

    def get_queryset(self):
        c_uid = self.kwargs['c_uid']
        return Lecture.objects.filter(chapter__uid=c_uid)

    def get_object(self):

        if not self.request.user.is_teacher:
            raise PermissionDenied()

        lecture = super().get_object()

        if (lecture is None) or lecture.chapter.subject.batch.institute != self.request.user.institute:
            raise NotFound()

        return lecture
