from rest_framework.views import APIView
from BaseSecurity.utils import JWT_auth, Key_Generator
from BaseSecurity.permissions import isAutorized, isSuperUser
from BaseSecurity.services import SecureResponse
from .serializers import ApiKeySerializer
from User.serializers import UserSerializer
from User.models import User
from .models import Api_key

class CreateApiKey(APIView):

    serializer_class = ApiKeySerializer
    permission_classes = [isSuperUser]

    def get(self, request): 
        user = JWT_auth.jwt_to_user(JWT_auth.get_jwt(request))

        if user == None: return SecureResponse(request=request, status=400)

        key_name = 'SuperApiKey'
        help_text = f'Api-key of user: {user.username}'

        try: key_name = request.GET['key_name']
        except: pass
        try: help_text = request.GET['help_text']
        except: pass

        key = Key_Generator.generate_user_api_key(user=user, help_text=help_text, key_name=key_name)
        
        key = Api_key.objects.last()

        return SecureResponse(request=request, data={"ApiKey": self.serializer_class(instance=key).data}, status=200)
    
class DeleteApiKey(APIView):
    
    serializer_class = ApiKeySerializer
    permission_classes = [isSuperUser]

    def get(self, request):
        key_id = request.GET['key_id']

        key = None
        try: key = Api_key.objects.get(id=key_id)
        except: return SecureResponse(request=request, status=400)

        user = JWT_auth.jwt_to_user(JWT_auth.get_jwt(request))

        if key.user.id == user.id:
            key.del_key()
        else: return SecureResponse(request=request, status=403)

        return SecureResponse(request=request, status=200)
    
class UpdateApiKey(APIView):

    serializer_class = ApiKeySerializer
    permission_classes = [isAutorized]

    def get(self, request):
        key_id = request.GET['key_id']
        key_value = None

        try: key_value = request.GET['key_value']
        except: pass
       
        key = None
        try: key = Api_key.objects.get(id=key_id)
        except: return SecureResponse(request=request, status=400)

        user = JWT_auth.jwt_to_user(JWT_auth.get_jwt(request))

        if key.user.id == user.id:
            key.del_key()
        else: return SecureResponse(request=request, status=403)

        if key_value != None:
            key.update_key(key_value)
        else: key.update_key_random()

        return SecureResponse(request=request, data={"ApiKey": self.serializer_class(instance=key).data}, status=200)
    

class ShowMyApiKeys(APIView):

    serializer_class = ApiKeySerializer
    permission_classes = [isAutorized]

    def get(self, request):
        user = JWT_auth.jwt_to_user(JWT_auth.get_jwt(request))

        keys = None

        try: keys = Api_key.objects.filter(user=user)
        except: return SecureResponse(request=request, status=400)

        return SecureResponse(request=request, data={"ApiKeys": self.serializer_class(instance=keys, many=True).data}, status=200)

class ShowUserApiKeys(APIView):

    serializer_classes = [ApiKeySerializer, UserSerializer]
    permission_classes = [isSuperUser]

    def get(self, request):
        user_id = request.GET['user_id']

        user = None
        keys = None

        try: user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)

        try: keys = Api_key.objects.filter(user=user)
        except: return SecureResponse(request=request, status=400)

        return SecureResponse(request=request, data={"User": self.serializer_class[1](instance=user).data,"ApiKeys": self.serializer_class[0](instance=keys, many=True).data}, status=200)
    
class DecryptKey(APIView):

    serializer_classes = ApiKeySerializer
    permission_classes = [isAutorized]

    def get(self, request):
        key_id = request.GET['key_id']

        key = None
        try: key = Api_key.objects.get(id=key_id)
        except: return SecureResponse(request=request, status=400)

        user = JWT_auth.jwt_to_user(JWT_auth.get_jwt(request))

        if key.user.id == user.id:
            return SecureResponse(request=request, data={"DecryptKey": key.key}, status=200)
        else: return SecureResponse(request=request, status=403)