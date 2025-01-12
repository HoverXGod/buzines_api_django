from .models import AuditLog
from .utils import JWT_auth
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

class AuditLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        action = request.get_full_path_info()
        request.log = AuditLog._write_audit(request=request, action=action)
        return self.get_response(request)

class AuthenticationMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        user = None

        token = JWT_auth.get_jwt(request)

        if token == None: return self.get_response(request)

        try:
            user = JWT_auth.jwt_to_user(jwt_token=token)

            if JWT_auth.verify_jwt_token(token):
                user.is_active = True
                request.user = user 

            else: 
                request.user = AnonymousUser()
                user.is_active = False

            user.save()            
    
        except:
            return self.get_response(request)

        return self.get_response(request)