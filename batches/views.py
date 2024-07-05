from rest_framework.generics import CreateAPIView, ListAPIView
from core.permissions import IsTeacher
from .models import Batch, Chapter, Subject, Enrollment
from .serializers import BatchSerializer, ChapterSerializer, SubjectSerializer


class GetBatches(ListAPIView):
    serializer_class = BatchSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_teacher:
            return Batch.objects.all()

        enrolled = Enrollment.objects.filter(user=user)

        return Batch.objects.filter(pk__in=enrolled)


class GetSubjects(ListAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        batch_id = self.kwargs['batch_id']
        return Subject.objects.filter_for_user(self.request.user, batch_id)


class GetChapters(ListAPIView):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        subject_id = self.kwargs['subject_id']
        subject = Subject.objects.get(uid=subject_id)
        return Chapter.objects.filter_for_user(self.request.user, subject.batch.uid)


class CreateBatch(CreateAPIView):
    permission_classes = [IsTeacher]
    serializer_class = BatchSerializer


class CreateSubject(CreateAPIView):
    permission_classes = [IsTeacher]
    serializer_class = SubjectSerializer


class CreateChapter(CreateAPIView):
    permission_classes = [IsTeacher]
    serializer_class = ChapterSerializer
