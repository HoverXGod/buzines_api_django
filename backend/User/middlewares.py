from BaseSecurity.services import SessionManager
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from BaseSecurity.utils import JWT_auth
from .models import User

class AuthenticationMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request.session.items(), '_auth_user_id'):
            request.user = User.objects.get(pk=request.session['_auth_user_id'])
            return self.get_response(request)

        token = JWT_auth.get_jwt(request)
        if not token:
            request.user = AnonymousUser()
            return self.get_response(request)

        else:
            cache_id = cache.get(token)
            if cache_id:
                sm = SessionManager(request)
                request.user = User.objects.get(pk=cache_id)
                request.user.is_active = True
                request.user.save()

                sm.auth__session()
                sm.auth__user(request.user)
                sm.auth__token(token)
                request = sm.get_request()
                del sm
                return self.get_response(request)

        sm = SessionManager(request)

        if JWT_auth.verify_jwt_token(token):
            user = JWT_auth.jwt_to_user(jwt_token=token)
            user.is_active = True
            user.save()
            sm.auth__session()

        else:
            request.token = None
            user = AnonymousUser()

        sm.auth__user(user)
        sm.auth__token(token)
        request = sm.get_request()
        del sm
        return self.get_response(request)

class ForceSessionSaveMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Принудительно сохраняем сессию если она изменена
        if hasattr(request, 'session') and request.session.modified:
            request.session.save()

        return response