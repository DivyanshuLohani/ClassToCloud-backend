from rest_framework.exceptions import ParseError
from rest_framework.views import APIView, Response
from core.serializers import UserSerializer
from .serializers import UserRegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import AllowAny

# Create your views here.
User = get_user_model()


class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):

        user_register_serializer = UserRegisterSerializer(data=request.data)
        user_register_serializer.is_valid(raise_exception=True)

        user = user_register_serializer.save()
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=201)


class UserView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):

        return self.request.user
