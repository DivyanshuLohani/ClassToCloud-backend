from rest_framework import serializers
from documents.serializers import NoteSerializer, DPPSerializer
from .models import Lecture


class LectureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lecture
        fields = '__all__'
        extra_kwargs = {
            'type': {'read_only': True}
        }
