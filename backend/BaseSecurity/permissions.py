from rest_framework.permissions import BasePermission
from BaseSecurity.utils import JWT_auth
from User.models import User

class isAnonymous(BasePermission):
    name="Anonymous"
    codename="anonym"

    def has_permission(self, request, view):
        return request.user.is_anonymous

class isAutorized(BasePermission):
    name="Authorized"
    codename="auhtor"

    def has_permission(self, request, view): 
        return request.user.is_authenticated
    
class isAdmin(BasePermission):
    name="Administrator"
    codename="admin"

    def has_permission(self, request, view):
        jwt_token = request.token

        if jwt_token == None: return False

        permissions = JWT_auth.get_user_permissions(jwt_token=jwt_token)

        if "super" in permissions: 
            return True

        if "admin" in permissions: 
            return True
    
class isModerator(BasePermission):
    name="Moderator"
    codename="moder"

    def has_permission(self, request, view):
        jwt_token = request.token

        if jwt_token == None: return False

        permissions = JWT_auth.get_user_permissions(jwt_token=jwt_token)

        if "super" in permissions: 
            return True
            
        if "moder" in permissions: 
            return True
    
class isSuperUser(BasePermission):
    name="SuperUser"
    codename="super"

    def has_permission(self, request, view):
        jwt_token = request.token

        if jwt_token == None: return False

        permissions = JWT_auth.get_user_permissions(jwt_token=jwt_token)

        if "super" in permissions:
            if not JWT_auth.verify_super_jwt(jwt_token=jwt_token): 
                return False
            else: return True
        else: return False
    
PERMISSIONS = {
    "Anonym": isAnonymous,
    "SuperUser": isSuperUser,
    "Moderator": isModerator,
    "Administrator":isAdmin,
    "Autorized": isAutorized,
}