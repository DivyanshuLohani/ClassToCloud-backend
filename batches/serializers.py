from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotFound
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

    def create(self, validated_data):
        batch_id = validated_data.pop('batch')
        batch = Batch.objects.filter(uid=batch_id)
        user = self.context['request'].user
        if not batch.exists() or not batch.first().institute == user.institute:
            raise NotFound("Batch not found.")

        return super().create(validated_data)


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

    def create(self, validated_data):
        sub_id = validated_data.pop('subject')
        subject = Batch.objects.filter(uid=sub_id)
        user = self.context['request'].user
        if not subject.exists() or not subject.first().batch.institute == user.institute:
            raise NotFound("Subject not found.")

        return super().create(validated_data)
