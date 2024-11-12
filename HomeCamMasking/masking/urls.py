# masking/urls.py

from django.urls import path
from .views import mask_video_frame

urlpatterns = [
    path('mask_video_frame/', mask_video_frame, name='mask_video_frame'),
]
