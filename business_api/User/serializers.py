from rest_framework import serializers
from .models import User, UserGroup, UserGroupItem

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_staff']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 1
        fields = ['id', 'username', 'email', 'last_login', 'addres','date_joined', 'isAdministrator', 'isModerator', 'is_superuser', 'phone_number']

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        depth = 1
        fields = '__all__'

class UserGroupItemSerializer(serializers.ModelSerializer):

    group = UserGroupSerializer
    user = UserSerializer

    class Meta:
        model = UserGroupItem
        depth = 1
        fields = '__all__'
