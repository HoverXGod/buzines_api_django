from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 1
        fields = ['id', 'username', 'email', 'base_password', 'date_joined', 'isAdministrator', 'isModerator', 'is_superuser', 'phone_number']