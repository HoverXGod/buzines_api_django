from BaseSecurity.services import SessionManager
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
class AuthenticationMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        token = JWT_auth.get_jwt(request)
        if token == None:
            request.user = AnonymousUser()
            return self.get_response(request)

        sm = SessionManager(request)
        sm.auth__token(token)

        if JWT_auth.verify_jwt_token(token):
            user = JWT_auth.jwt_to_user(jwt_token=token)
            user.is_active = True
            user.save()
            sm.auth__session()

        else:
            request.token = None
            user = AnonymousUser()

        sm.auth__user(user)
        request = sm.get_request()
        del sm
        return self.get_response(request)