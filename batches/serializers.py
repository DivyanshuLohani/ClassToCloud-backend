from rest_framework.serializers import ModelSerializer
from .models import Batch, Subject, Chapter


class AddInstituteMixin:

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['institute'] = user.institute
        return super().create(validated_data)


class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'uid', 'name', 'batch']  # Add other fields if needed


class BatchSerializer(ModelSerializer, AddInstituteMixin):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Batch
        fields = ['id', 'uid', 'name', 'description',
                  'is_active', 'start_date', 'end_date', 'subjects']


class ChapterSerializer(ModelSerializer):

    class Meta:
        model = Chapter
        fileds = "__all__"
