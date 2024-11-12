# masking/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('mask_video_frame/', views.mask_video_frame, name='mask_video_frame'),
]