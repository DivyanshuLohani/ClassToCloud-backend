from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import shortuuid


def institute_upload(instance, filename):
    return f"uploads/{instance.uid}/{filename}"


class BaseModel(models.Model):

    class Meta:
        abstract = True

    id = None
    uid = models.CharField(max_length=64, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.pk:
            class_name_prefix = self.__class__.__name__ + '_'
            self.uid = class_name_prefix.lower() + shortuuid.uuid()

        super().save(*args, **kwargs)

    @property
    def id(self) -> str:
        return self.uid


class Institute(BaseModel):
    name = models.CharField(max_length=256)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    website = models.URLField(blank=True)  # Optional website field
    image = models.ImageField(
        upload_to=institute_upload, blank=True, null=True
    )
    description = models.TextField(blank=True)  # Longer description
    # Dictionary for social media links
    social_media_links = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel):

    first_name = None
    last_name = None
    username = None
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    standard = models.CharField(max_length=10, default=None, null=True)
    phone_number = PhoneNumberField(region="IN", default=None, null=True)
    meta = models.JSONField("MetaData", default=dict)

    institute = models.ForeignKey(
        Institute, on_delete=models.PROTECT, related_name="users", null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def __str__(self) -> str:
        return self.name
