from rest_framework import serializers
from User.serializers import UserSerializer
from .models import Api_key

class UserApiKeySerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = Api_key
        depth = 1
        fields = ['id', 'key_name', 'key_value', 'user', 'help_text', 'is_active', 'created_at', 'updated_at']

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Api_key
        depth = 1
        fields = ['id', 'key_name', 'key_value', 'help_text', 'is_active', 'created_at', 'updated_at']