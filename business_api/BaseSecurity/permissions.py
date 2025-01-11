from rest_framework.permissions import BasePermission
from BaseSecurity.utils import JWT_auth


class isAutorized(BasePermission):
    name="Authorized"
    codename="auhtor"

    def has_permission(self, request, view): return JWT_auth.verify_jwt_token(jwt_token=JWT_auth.get_jwt(request=request))
    
class isAdmin(BasePermission):
    name="Administrator"
    codename="admin"

    def has_permission(self, request, view):
        jwt_token = JWT_auth.get_jwt(request)

        if not JWT_auth.verify_jwt_token(jwt_token=jwt_token): return False

        permissions = JWT_auth.get_user_permissions(jwt_token=jwt_token)

        if "super" in permissions: 
            if not JWT_auth.verify_super_jwt(jwt_token=jwt_token): 
                return False
            else: return True

        if "admin" in permissions: 
            if not JWT_auth.verify_super_jwt(jwt_token=jwt_token): 
                return False
            else: return True
        else: return False
    
class isModerator(BasePermission):
    name="Moderator"
    codename="moder"

    def has_permission(self, request, view):
        jwt_token = JWT_auth.get_jwt(request)
        
        if not JWT_auth.verify_jwt_token(jwt_token=jwt_token): return False

        permissions = JWT_auth.get_user_permissions(jwt_token=jwt_token)

        if "super" in permissions: 
            if not JWT_auth.verify_super_jwt(jwt_token=jwt_token): 
                return False
            else: return True
            
        if "moder" in permissions: 
            if not JWT_auth.verify_super_jwt(jwt_token=jwt_token): 
                return False
            else: return True
        else: return False
    
class isSuperUser(BasePermission):
    name="SuperUser"
    codename="super"

    def has_permission(self, request, view):
        jwt_token = JWT_auth.get_jwt_super(request)

        if not JWT_auth.verify_jwt_token(jwt_token=jwt_token): return False

        permissions = JWT_auth.get_user_permissions(jwt_token=jwt_token)

        if "super" in permissions:
            if not JWT_auth.verify_super_jwt(jwt_token=jwt_token): 
                return False
            else: return True
        else: return False
    
PERMISSIONS = {
    "SuperUser": isSuperUser,
    "Moderator": isModerator,
    "Administrator":isAdmin,
    "Autorized": isAutorized,
}