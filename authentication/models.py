from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class VerifyCode(models.Model):
    code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(hours=1)
    )
