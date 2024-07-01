from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import shortuuid


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


class User(AbstractUser, BaseModel):

    first_name = None
    last_name = None
    username = None
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    standard = models.CharField(max_length=10, default=None, null=True)
    phone_number = PhoneNumberField(region="IN", default=None, null=True)
    meta = models.JSONField("MetaData", default=dict)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def __str__(self) -> str:
        return self.name

    @property
    def id(self):
        return self.uid
