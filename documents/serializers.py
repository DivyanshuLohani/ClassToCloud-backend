from rest_framework import serializers
from .models import Note, DPP
from core.mixins import SignedFileFieldMixin


class NoteSerializer(serializers.ModelSerializer, SignedFileFieldMixin):

    class Meta:
        model = Note
        fields = ['uid', 'lecture', 'chapter', 'batch',
                  'name', 'file', 'created_at', 'updated_at']


class DPPSerializer(serializers.ModelSerializer, SignedFileFieldMixin):
    class Meta:
        model = DPP
        fields = ['uid', 'lecture', 'chapter', 'batch',
                  'name', 'file', 'created_at', 'updated_at']
