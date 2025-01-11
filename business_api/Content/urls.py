from django.urls import path
from .views import *

urlpatterns = [
    path('api/content/get_post', GetPost.as_view()),
    path('api/content/get_all_posts', GetPosts.as_view()),
    path('api/content/add_post', CreatePost.as_view()),
    path('api/content/edit_post', UpdatePost.as_view()),
    path('api/content/add_image', AddImagePost.as_view()),


]
