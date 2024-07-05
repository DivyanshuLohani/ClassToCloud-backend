from rest_framework.generics import CreateAPIView, ListAPIView
from core.permissions import IsTeacher
from .models import Batch, Chapter, Subject, Enrollment
from .serializers import BatchSerializer, ChapterSerializer, SubjectSerializer
from documents.serializers import NoteSerializer, DPPSerializer
from lectures.serializers import LectureSerializer


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


class ListChapterNotes(ListAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        chapter = Chapter.objects.filter(uid=self.kwargs['uid']).first()
        chapter.check_permissions(self.request.user)
        return chapter.notes.all()


class ListChapterDPPs(ListAPIView):
    serializer_class = DPPSerializer

    def get_queryset(self):
        chapter = Chapter.objects.filter(uid=self.kwargs['uid']).first()
        chapter.check_permissions(self.request.user)
        return chapter.dpps.all()


class ListChapterLectures(ListAPIView):
    serializer_class = LectureSerializer

    def get_queryset(self):
        chapter = Chapter.objects.filter(uid=self.kwargs['uid']).first()
        chapter.check_permissions(self.request.user)
        return chapter.lectures.all()
