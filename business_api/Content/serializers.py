from rest_framework import serializers
from .models import Post
from User.serializers import UserSerializer

class PageTextSerializers(serializers.ModelSerializer): pass

class PostSerializer(serializers.ModelSerializer):
    
    user = UserSerializer()
    author = UserSerializer()

    class Meta:
        model = Post
        depth = 1
        fields = ['title', 'text', 'author', 'created_at', 'updated_at', 'id', 'images']