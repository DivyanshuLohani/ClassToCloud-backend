from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
import shortuuid


def institute_upload(instance, filename):
    return f"uploads/{instance.uid}/{filename}"


class BaseModel(models.Model):

    class Meta:
        abstract = True

    id = None
    uid = models.CharField(max_length=64, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.pk:
            class_name_prefix = self.__class__.__name__ + '_'
            self.uid = class_name_prefix.lower() + shortuuid.uuid()

        super().save(*args, **kwargs)


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


class UserManager(BaseUserManager):

    def create_superuser(self, email, password, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create(self, **kwargs: Any) -> Any:
        password = kwargs.pop("password")
        self.set_password(password)
        return super().create(**kwargs)


class User(AbstractUser, BaseModel):

    first_name = None
    last_name = None
    username = None
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    standard = models.CharField(
        max_length=10, default=None, null=True, blank=True)
    phone_number = PhoneNumberField(region="IN", default=None, null=True)
    meta = models.JSONField("MetaData", default=dict, blank=True, null=True)

    is_teacher = models.BooleanField(default=False)

    institute = models.ForeignKey(
        Institute, on_delete=models.PROTECT, related_name="users", null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            self.set_password(self.password)

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
