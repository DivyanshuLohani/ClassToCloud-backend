from .models import Note, DPP
from .serializers import NoteSerializer, DPPSerializer
from core.permissions import IsTeacher, OnlyTeacherUpdate
from rest_framework import generics, exceptions


class CreateNotesView(generics.CreateAPIView):
    permission_classes = [IsTeacher]
    serializer_class = NoteSerializer

    def perform_create(self, serializer):
        note = serializer.save()
        if note.batch.institute != self.request.user.institute:
            note.delete()
            raise exceptions.NotFound("Batch not found")


class NotesView(generics.RetrieveAPIView):
    permission_classes = [OnlyTeacherUpdate]
    serializer_class = NoteSerializer

    def get_object(self):
        obj = generics.get_object_or_404(Note, uid=self.kwargs['uid'])
        if obj and obj.batch.institute != self.request.user.institute:
            raise exceptions.NotFound()

        return obj


class CreateDPPView(generics.CreateAPIView):
    permission_classes = [IsTeacher]
    serializer_class = DPPSerializer

    def perform_create(self, serializer):
        dpp = serializer.save()
        if dpp.batch.institute != self.request.user.institute:
            dpp.delete()
            raise exceptions.NotFound("Batch not found")


class DPPView(generics.RetrieveAPIView):
    permission_classes = [OnlyTeacherUpdate]
    serializer_class = DPPSerializer

    def get_object(self):
        obj = generics.get_object_or_404(DPP, uid=self.kwargs['uid'])
        if obj and obj.batch.institute != self.request.user.institute:
            raise exceptions.NotFound()

        return obj
