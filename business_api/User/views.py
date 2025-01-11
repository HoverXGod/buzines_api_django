from rest_framework.views import APIView
from BaseSecurity.utils import JWT_auth
from BaseSecurity.permissions import isAutorized, isSuperUser, isAdmin
from BaseSecurity.services import SecureResponse
from .serializers import UserSerializer
from Api_Keys.serializers import ApiKeySerializer
from Api_Keys.models import Api_key
from .models import User


class RegisterUser(APIView):
    
    serializer_class = UserSerializer

    def get(self, request):

        password = request.GET["password"]
        username = request.GET["login"]
        email = request.GET["email"]
        name = request.GET["name"]

        answer = User.register_user(login=username, password=password, first_name=name)

        jwt_token = User.login_user_by_password(request, email=email, password=password)

        if answer == None: return SecureResponse(request=request, status=400)
        return SecureResponse(request=request, data={"JsonWebToken":str(jwt_token), "UserData": self.serializer_class(instance=answer).data}, status=200)

class loginUser(APIView):
    
    serializer_class = UserSerializer
    
    def get(self, request):
        """Метод для входа в аккаунт, возвращает JWT Токен личной разработки, который активен именно в тот день, в который выдан"""

        password = request.GET["password"]
        login = request.GET["login"]

        jwt_token = User.login_user_by_password(request, login=login, password=password)
        if jwt_token == None: return SecureResponse(request=request, status=400)
        else: return SecureResponse(request=request, data={"JsonWebToken":str(jwt_token)})

class MyProfile(APIView):

    serializer_class = UserSerializer
    permission_classes = [isAutorized]

    def get(self, request):
        jwt = JWT_auth.get_jwt(request)
        user = JWT_auth.jwt_to_user(jwt_token=jwt)

        api_keys = Api_key.objects.filter(user=user)

        return SecureResponse(request=request, data={ 'UserData': self.serializer_class(instance=user).data, 'ApiKeys':ApiKeySerializer(instance=api_keys, many=True).data}, status=200)

class UserProfile(APIView):

    serializer_class = UserSerializer
    permission_classes = [isSuperUser]

    def get(self, request):
        user_id = request.GET['user_id']
        user = None
        
        try: user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)

        api_keys = Api_key.objects.filter(user=user)

        return SecureResponse(request=request, data={ 'UserData': self.serializer_class(instance=user).data, 'ApiKeys':ApiKeySerializer(instance=api_keys, many=True).data}, status=200)

class EditProfileUser(APIView):

    serializer_class = UserSerializer
    permission_classes = [isAutorized]

    def get(self, request):
        user_id = JWT_auth._decompile_jwt_token_list(JWT_auth.get_jwt(request))[0]
        try:
            user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)
        
        phone_number = None
        password = None
        username = None
        email = None
        old_password = None

        try: phone_number = request.GET['phone_number']
        except: pass
        try: password = request.GET['password']
        except: pass
        try: username = request.GET['username']
        except: pass
        try: email = request.GET['email']
        except: pass
        try: old_password = request.GET['old_password']
        except: pass
        try: first_name = request.GET['first_name']
        except: pass
        try: last_name = request.GET['last_name']
        except: pass

        answer = user.edit_profile(last_name=last_name, first_name=first_name, name=username, old_pasword=old_password, password=password, email=email, phone_number=phone_number)
        if answer: 
            user = User.objects.get(id=user_id)
            return SecureResponse(request=request, data={"UserData": self.serializer_class(instance=user).data}, status=200)
        else: return SecureResponse(request=request, status=400)

class SetSuperUser(APIView):

    serializer_class = UserSerializer
    permission_classes = [isSuperUser]

    def get(self, request):
        user_id = request.GET['user_id']
        try: user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)
        
        user.super_user = request.GET['bool_value']

        return SecureResponse(request=request, status=200)
    
class SetAdministratorUser(APIView):

    serializer_class = UserSerializer
    permission_classes = [isSuperUser]

    def get(self, request):
        user_id = request.GET['user_id']
        try: user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)
        
        user.is_admin = request.GET['bool_value']

        return SecureResponse(request=request, status=200)
    
class SetModeratorrUser(APIView):

    serializer_class = UserSerializer
    permission_classes = [isAdmin]

    def get(self, request):
        user_id = request.GET['user_id']
        try: user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)
        
        user.is_moderator = request.GET['bool_value']
        
        return SecureResponse(request=request, status=200)
    
class DeleteUser(APIView):

    serializer_class = UserSerializer
    permission_classes = [isSuperUser]

    def get(self, request):
        user_id = request.GET['user_id']
        user = None
        try:
            user = User.objects.get(id=user_id)
        except: return SecureResponse(request=request, status=400)

        if user.is_superuser == False:
            user.del_user()
        else: return SecureResponse(request=request, status=403)

        return SecureResponse(request=request, status=200)