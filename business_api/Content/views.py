from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser
from BaseSecurity.services import SecureResponse
from .serializers import PostSerializer
from .models import Post

class GetAuthorPost(APIView): pass

class GetPost(APIView): pass

class CreatePost(APIView): pass

class UpdatePost(APIView): pass

class GetPosts(APIView): pass
