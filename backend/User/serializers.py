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
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'address', 'date_joined', 'phone_number', 'currency', 'user_type']

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
