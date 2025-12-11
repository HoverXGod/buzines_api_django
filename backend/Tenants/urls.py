from django.urls import path
from .views import *

urlpatterns = [
    path('api/tenants/db_ready', DataBaseReady.as_view()),
]