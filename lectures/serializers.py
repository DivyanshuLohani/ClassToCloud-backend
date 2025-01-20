from rest_framework import serializers
from batches.models import Chapter
from documents.serializers import NoteSerializer, DPPSerializer
from .models import Lecture


class UploadInitalizerSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=255)
    chapter = serializers.PrimaryKeyRelatedField(
        queryset=Chapter.objects.all()
    )


class UploadChunkSerializer(serializers.Serializer):

    file = serializers.FileField()
    upload_id = serializers.CharField()
    part_number = serializers.IntegerField()
    uid = serializers.CharField()


class CreateLectureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lecture
        fields = ['uid', 'chapter', 'title', 'type', 'file', 'status']
        extra_kwargs = {
            'status': {'read_only': True},
            'type': {'read_only': True},
            'file': {'write_only': True},
        }


class LectureSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)
    dpps = DPPSerializer(many=True, read_only=True)
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        if obj.type == 'native':
            return obj.file.url
        else:
            return None

    class Meta:
        model = Lecture
        fields = '__all__'
        extra_kwargs = {
            'chapter': {'read_only': True},
            'file': {'read_only': True},
            'video_id': {'read_only': True},
            'duration': {'read_only': True},
            'status': {'read_only': True},
        }
