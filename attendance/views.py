from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ParseError
from .serializer import AttendanceSerializer
from core.permissions import IsTeacher
from core.models import User
from .models import Attendance
from rest_framework.response import Response
# Create your views here.


class AddAttendance(CreateAPIView):

    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher]

    def perform_create(self, serializer):
        serializer.save(institute=self.request.user.institute, present=True)


class AddAttendanceBullk(APIView):

    permission_classes = [IsTeacher]

    def post(self, request):
        attendance_data = request.data
        if not attendance_data or not attendance_data.get("users") or not attendance_data.get("date"):
            raise ParseError()
        institute = self.request.user.institute
        users = User.objects.filter(uid__in=attendance_data['users'])
        attendance_objs = []
        for i in users:
            a = Attendance(user=i, institute=institute,
                           date=attendance_data["date"], present=True)
            attendance_objs.append(a)
        Attendance.objects.bulk_create(attendance_objs)

        return Response(status=201)


class GetAttendance(RetrieveAPIView):

    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        objs = Attendance.objects.filter(
            instititute=self.request.user.institute
        )
        return objs

# class GetUserAttendance(RetrieveAPIView):
#     serializer_class = AttendanceSerializer

#     def get_object(self):
#         user_id =
#         o = Attendance.objects.filter()
