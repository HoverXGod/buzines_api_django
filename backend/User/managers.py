from .models import UserGroup, UserGroupItem

class UserGroupManager: 
    
    @staticmethod
    def get_user_group(user): 
        return UserGroup.get_user_groups__list(user=user)

    @staticmethod
    def add_user_to_group(user, group): 
        UserGroupItem.objects.create(user=user, group=group)

        return UserGroupItem.objects.last()

    @staticmethod
    def get_user_group_permissions(user): 
        items = UserGroup.get_user_groups__list(user)

        return [item.permissions_list for item in items]

    @staticmethod 
    def set_group_permissions(group, permissions): 
        UserGroup.permissions_list = permissions

        return None

    @staticmethod
    def get_users_in_group(group): 
        return [ item.user for item in UserGroupItem.objects.filter(group=group)]