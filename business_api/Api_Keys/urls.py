from django.urls import path
from .views import *

urlpatterns = [
    path('api/key/create', CreateApiKey.as_view()),
    path('api/key/delete', DeleteApiKey.as_view()),
    path('api/key/update', UpdateApiKey.as_view()),
    path('api/key/get_keys', ShowMyApiKeys.as_view()),
    path('api/key/get_user_keys', ShowMyApiKeys.as_view()),
    path('api/key/decrypt_key', DecryptKey.as_view()),
]