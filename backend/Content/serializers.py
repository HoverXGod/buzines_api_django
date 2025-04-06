from rest_framework import serializers
from .models import Post, PageText
from User.serializers import AuthorSerializer

class PageTextSerializers(serializers.ModelSerializer): 
    
    class Meta:
        model = PageText
        fields = ['id', 'index', 'page_name', 'text']

class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()

    class Meta:
        model = Post
        depth = 1
        fields = ['id', 'title', 'text', 'author', 'created_at', 'updated_at', 'id', 'images']