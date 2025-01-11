from django.urls import path
from .views import *

urlpatterns = [
    path('api/CRM/create_page_text', CreatePageText.as_view()),
    path('api/CRM/update_page_text', UpdatePageText.as_view()),
    path('api/CRM/get_all', GetPageTexts.as_view()),
    path('api/CRM/delete_page_text', DeletePageText.as_view()),
    path('api/CRM/delete_page_texts', DeletePageTexts.as_view()),
]
