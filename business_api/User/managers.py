from .models import User, UserGroup, UserGroupItem

class UserGroupManager: 
    
    @staticmethod
    def get_user_group(user): pass

    @staticmethod
    def add_user_to_group(user, group): pass

    @staticmethod
    def get_user_group_permissions(user): pass

    @staticmethod 
    def set_user_group_permissions(user, permissions): pass\
    
    @staticmethod
    def get_users_in_group(group): pass