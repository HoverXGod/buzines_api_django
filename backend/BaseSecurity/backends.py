from django.contrib.auth.backends import BaseBackend
from .utils import JWT_auth
from User.models import User

class AuthenticateLogin(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        token, _ = User.login_user_by_password(request, login=username, password=password)
        return JWT_auth.jwt_to_user(token) if not token == None else None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        
    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_superuser


class AuthenticateToken(BaseBackend):
    def authenticate(self, request, token=None): 
        try: return JWT_auth.jwt_to_user(jwt_token=token)
        except:
            try: return JWT_auth.jwt_to_user(jwt_token=JWT_auth.get_jwt(request=request))
            except: pass
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
    def has_perm(self, user_obj, perm, obj=None):
        return user_obj.is_superuser