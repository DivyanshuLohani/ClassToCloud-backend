from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Batch, Chapter, Subject, Enrollment
from .serializers import BatchSerializer


class GetBatches(ListAPIView):
    serializer_class = BatchSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Batch.objects.all()

        enrolled = user.enrollment_set.all().values_list('batch__id', flat=True)
        return Batch.objects.filter(pk__in=enrolled)


class GetSubjects(ListAPIView):
    def get_queryset(self):
        batch_id = self.kwargs['batch_id']
        return Subject.objects.filter_for_user(self.request.user, batch_id)


class GetChapters(ListAPIView):

    def get_queryset(self):
        subject_id = self.kwargs['subject_id']
        subject = Subject.objects.get(uid=subject_id)
        return Chapter.objects.filter_for_user(self.request.user, subject.batch.uid)
