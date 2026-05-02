from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/status/(?P<user_id>\d+)/$', consumers.VMConnect.as_asgi()),
]
