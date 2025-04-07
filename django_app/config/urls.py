"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from simulator.views import health_check
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve
from simulator import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('', include('simulator.urls')),
    path('test-media/', views.test_media),
    path('partials/<str:page_name>/', views.partial_view, name='partial'),
    path('api/generate-music/', views.generate_music, name='generate_music'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)