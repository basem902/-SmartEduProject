"""
WebSocket URL routing for projects app
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/telegram-send/(?P<project_id>\d+)/$', consumers.TelegramSendConsumer.as_asgi()),
]
