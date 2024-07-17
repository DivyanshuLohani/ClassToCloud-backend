from django.db import models
from core.models import BaseModel
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, NotFound
from core.models import Institute


class SubjectPermissionManager(models.Manager):
    def filter_for_user(self, user, batch_id):
        batch = Batch.objects.filter(uid=batch_id).first()
        if not batch or not batch.institute == user.institute:
            raise NotFound("Batch not found")
        if user.is_staff or user.is_teacher:
            return self.filter(batch__uid=batch_id)
        else:
            enrollment = Enrollment.objects.filter(
                user=user, batch=batch)
            if not enrollment.exists():
                raise PermissionDenied(
                    "You do not have permission to view this batch")
            return self.filter(batch__uid=batch_id)


class ChapterPermissionManager(models.Manager):
    def filter_for_user(self, user, batch_id):
        batch = Batch.objects.filter(uid=batch_id).first()
        if not batch or not batch.institute == user.institute:
            raise NotFound("Batch not found")
        if user.is_staff or user.is_teacher:
            return self.filter(subject__batch=batch)
        else:
            enrollment = Enrollment.objects.filter(
                user=user, batch=batch)
            if not enrollment.exists():
                raise PermissionDenied(
                    "You do not have permission to view this batch"
                )
            return self.filter(subject__batch=batch_id)


def one_year_from_now(): timezone.now() + timezone.timedelta(weeks=53)


class Batch(BaseModel):

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256)

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="batches", null=True
    )

    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(
        default=one_year_from_now)

    def __str__(self) -> str:
        return f"{self.name} ({self.description})"

    class Meta:
        ordering = ["-created_at"]


class Subject(BaseModel):

    batch = models.ForeignKey(Batch, models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=32)

    objects = SubjectPermissionManager()

    def __str__(self) -> str:
        return f"{self.name} - {self.batch}"

    class Meta:
        ordering = ["-created_at"]


class Chapter(BaseModel):

    name = models.CharField(max_length=32)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="chapters")

    objects = ChapterPermissionManager()

    def check_permissions(self, user):
        if self.subject.batch.institute != user.institute:
            raise NotFound()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-created_at"]


class Enrollment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'batch')
