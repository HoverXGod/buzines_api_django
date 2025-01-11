from django.urls import path
from .views import *

urlpatterns = [
    path('api/user/register', RegisterUser.as_view()),
    path('api/user/login', loginUser.as_view()),
    path('api/user/profile', MyProfile.as_view()),
    path('api/user/get_profile', UserProfile.as_view()),
    path('api/user/edit_profile', EditProfileUser.as_view()),
    path('api/user/set_super_user', SetSuperUser.as_view()),
    path('api/user/set_admin_user', SetAdministratorUser.as_view()),
    path('api/user/set_moder_user', SetModeratorrUser.as_view()),
    path('api/user/delete', DeleteUser.as_view()),
] 