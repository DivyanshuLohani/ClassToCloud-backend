from rest_framework.serializers import ModelSerializer, SerializerMethodField
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
        fields = ['uid', 'name', 'batch']  # Add other fields if needed

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
        fields = ['uid', 'name', 'description',
                  'is_active', 'start_date', 'end_date', 'subjects']


class ChapterSerializer(ModelSerializer):

    lectures = SerializerMethodField()
    notes = SerializerMethodField()
    dpps = SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ['uid', 'name', 'subject', 'lectures', 'notes', 'dpps']

    def get_lectures(self, instance):
        return len(instance.lectures.all())

    def get_notes(self, instance):
        return len(instance.notes.all())

    def get_dpps(self, instance):
        return len(instance.dpps.all())

    def create(self, validated_data):
        sub_id = validated_data.pop('subject')
        subject = Batch.objects.filter(uid=sub_id)
        user = self.context['request'].user
        if not subject.exists() or not subject.first().batch.institute == user.institute:
            raise NotFound("Subject not found.")

        return super().create(validated_data)
