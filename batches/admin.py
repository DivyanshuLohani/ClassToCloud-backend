from django.contrib import admin
from .models import Batch, Subject, Chapter
# Register your models here.
admin.site.register((Batch, Subject, Chapter))
