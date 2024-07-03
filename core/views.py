from rest_framework.authentication import authenticate
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import EmployeeSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from core.permissions import IsAdminUser

# Create your views here.


class CustomLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user
        employee = authenticate(username=username, password=password)
        if employee is not None:
            login(request, employee)
            # User authenticated successfully
            # You can perform additional checks or actions here if needed
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Invalid credentials
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomLogout(APIView):

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class CreateEmployee(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        outlet = request.user.outlet
        if serializer.is_valid():
            serializer.save(outlet=outlet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
