from rest_framework.serializers import Serializer, EmailField, CharField, ModelSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializar(Serializer):
    email = EmailField()
    password = CharField(max_length=1024)


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'standard', 'phone_number', 'password']

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data, institute=self.user.institute)
        user.set_password(password)
        return user
