from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from django.contrib import admin
from User.views import *


urlpatterns = [       
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'), 

    path('', include('User.urls')),
    path('', include('Api_Keys.urls')),
    path('', include('Content.urls')),
    path('', include('CRM.urls')),
]
