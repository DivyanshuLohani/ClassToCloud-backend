from rest_framework import serializers
from .models import Note, DPP


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['uid', 'lecture', 'chapter', 'batch',
                  'name', 'file', 'created_at', 'updated_at']


class DPPSerializer(serializers.ModelSerializer):
    class Meta:
        model = DPP
        fields = ['uid', 'lecture', 'chapter', 'batch',
                  'name', 'file', 'created_at', 'updated_at']
