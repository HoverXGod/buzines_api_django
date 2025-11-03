from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isModerator, isAdmin
from BaseSecurity.services import SecureResponse
from .serializers import PostSerializer
from User.serializers import AuthorSerializer
from .models import Post
from core.cache import cache_api_view
from django.utils.decorators import method_decorator

class GetAuthorPost(APIView): 

    serializer_class = AuthorSerializer
    permission_classes = []

    @method_decorator(cache_api_view(use_models=[Post]))
    def get(self, request):
        post_id = request.GET['post_id']
        
        try: post = Post.objects.get(psot_id=post_id)
        except: return SecureResponse(request=request, data="", status=400)
        
        author = post.author
        
        return SecureResponse(request=request, data=self.serializer_class(instance=author).data, status=200)

class GetPost(APIView): 

    serializer_class = PostSerializer
    permission_classes = []

    @method_decorator(cache_api_view(use_models=[Post]))
    def get(self, request):
        post_id = request.GET['post_id']

        try: post = Post.objects.get(psot_id=post_id)
        except: return SecureResponse(request=request, data="", status=400)

        return SecureResponse(request=request, data=self.serializer_class(instance=post).data, status=200)

class CreatePost(APIView): 

    serializer_class = PostSerializer
    permission_classes = [isModerator, isAdmin]

    def get(self, request):

        text = request.GET['text']
        title = request.GET['title']
        images = request.GET['images']
        user = request.user

        try:
            post = Post.create_post(
                text=text,
                author=user,
                images=images,
                title=title
            )
        except: return SecureResponse(request=request, data='', status=400)

        post = Post.objects.filter(author=user).last()
        
        return SecureResponse(request=request, data=self.serializer_class(instance=post).data, status=200)
    
class UpdatePost(APIView): 
    
    serializer_class = PostSerializer
    permission_classes = [isModerator, isAdmin]

    def get(self, request):
        post_id = request.GET['post_id']
        text = request.GET['text']
        title = request.GET['title']

        try: post = Post.objects.get(id=post_id)
        except: return SecureResponse(request=request, data='', status=400)

        post = post.update_post(text=text, title=title)

        return SecureResponse(request=request, data=self.serializer_class(instance=post).data, status=200)


class GetPosts(APIView): 
    
    serializer_class = PostSerializer

    @method_decorator(cache_api_view(use_models=[Post]))
    def get(self, request):
        posts = Post.objects.all()

        return SecureResponse(request=request, data=self.serializer_class(instance=posts, many=True).data, status=200)

class AddImagePost(APIView): 
    
    serializer_class = PostSerializer
    permission_classes = [isModerator, isAdmin]

    def get(self, request):
        post_id = request.GET['post_id']
        images = request.GET['images']

        try: post = Post.objects.get(id=post_id)
        except: return SecureResponse(request=request, data='', status=400)

        post = post.update_image(image=images)

        return SecureResponse(request=request, data=self.serializer_class(instance=post).data, status=200)

class DeletePost(APIView):
    serializer_class = PostSerializer
    permission_classes = [isSuperUser]

    def get(self, request):
        post_id = request.GET['post_id']

        try: post = Post.objects.get(id=post_id)
        except: return SecureResponse(request=request, data='', status=400)

        bufer_post = post

        post.del_post()

        return SecureResponse(request=request, data=self.serializer_class(instance=bufer_post).data, status=200)