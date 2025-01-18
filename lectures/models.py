from batches.models import Chapter
from core.models import BaseModel
from django.db import models


def video_upload(instance, filename):
    return f"lectures/{instance.uid}.{filename.split(".")[-1]}"


class Lecture(BaseModel):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="lectures"
    )

    title = models.CharField(max_length=255)
    type = models.CharField(
        choices=(("native", "Native"), ("youtube", "YouTube")), max_length=15)
    video_id = models.CharField(
        null=True, max_length=24  # if the type is youtube
    )
    duration = models.IntegerField(default=1)  # Duration in seconds
    file = models.FileField(upload_to=video_upload, null=True,
                            blank=True
                            )  # if the type is native
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), (
        'in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')

    class Meta:
        ordering = ("-created_at",)


class GoogleCredentials(models.Model):

    credentials = models.TextField()
