from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isModerator, isAdmin
from BaseSecurity.services import SecureResponse
from .serializers import PostSerializer
from User.serializers import AuthorSerializer
from .models import Post

class GetAuthorPost(APIView): 

    serializer_class = AuthorSerializer
    permission_classes = []

    def get(self, request):
        post_id = request.GET['post_id']
        
        try: post = Post.objects.get(psot_id=post_id)
        except: return SecureResponse(request=request, data="", status=400)
        
        author = post.author
        
        return SecureResponse(request=request, data=self.serializer_class(instance=author).data, status=200)

class GetPost(APIView): 

    serializer_class = PostSerializer
    permission_classes = []

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
        user = request.user

        try:
            post = Post.create_post(
                text=text,
                author=user,
                images='',
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

        try: Post.objects.get(id=post_id)
        except: return SecureResponse(request=request, data='', status=400)

        post = Post.update_post(text=text, title=title)

        return SecureResponse(request=request, data=self.serializer_class(instance=post).data, status=200)


class GetPosts(APIView): 
    
    serializer_class = PostSerializer

    def get(self, request):
        posts = Post.objects.all()

        return SecureResponse(request=request, data=self.serializer_class(instance=posts, many=True).data, status=200)

class AddImagePost(APIView): pass

class GetPagePosts(APIView): pass
