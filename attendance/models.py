from core.models import User, Institute
from django.db import models


class Attendance(models.Model):

    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'institute', 'date')
