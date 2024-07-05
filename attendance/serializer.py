from .models import Attendance
from rest_framework.serializers import ModelSerializer


class AttendanceSerializer(ModelSerializer):

    class Meta:
        model = Attendance
        fields = ['user', 'date', 'present']

        extra_kwargs = {
            'present': {'read_only': True}
        }
