# masking/routing.py

from django.urls import path
from .consumers import MaskConsumer

websocket_urlpatterns = [
    path('ws/mask/', MaskConsumer.as_asgi()),
]
