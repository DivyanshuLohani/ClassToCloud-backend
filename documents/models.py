from django.db import models
from core.models import BaseModel
from lectures.models import Lecture
from batches.models import Chapter, Batch


def note_upload_to(instance, filename):
    return f"notes/{instance.uid}.{filename.split(".")[-1]}"


def dpp_upload_to(instance, filename):
    return f"dpps/{instance.uid}.{filename.split(".")[-1]}"


class Note(BaseModel):

    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="notes")

    lecture = models.ForeignKey(
        Lecture, on_delete=models.SET_NULL,
        null=True, default=None,
        related_name="notes"
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.SET_NULL,
        null=True,
        related_name="notes"
    )

    name = models.CharField(max_length=50, default="")
    file = models.FileField(upload_to=note_upload_to)


class DPP(BaseModel):

    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="dpps"
    )

    lecture = models.ForeignKey(
        Lecture, on_delete=models.SET_NULL,
        null=True, default=None,
        related_name="dpps"
    )
    chapter = models.ForeignKey(
        Chapter, on_delete=models.SET_NULL,
        null=True,
        related_name="dpps"
    )
    name = models.CharField(max_length=50, default="")
    file = models.FileField(upload_to=dpp_upload_to)
