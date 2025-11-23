from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin


from BaseSecurity.services import SessionManager
from .models import AuditLog, ExceptionManager
from .utils import JWT_auth

class AuditLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        action = request.get_full_path_info()
        request.log = AuditLog._write_audit(request=request, action=action)
        return self.get_response(request)

class ErrorLogingMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as error:
            ExceptionManager.register_exception(error)