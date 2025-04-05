from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/eeg/', views.simulate_eeg, name='eeg-api'),
    path('api/set-emotion-profile/', views.set_emotion_profile, name='set-emotion-profile'),
    path('api/generate-music/', views.generate_music, name='generate-music'),
    path('test-write/', views.test_write),
]