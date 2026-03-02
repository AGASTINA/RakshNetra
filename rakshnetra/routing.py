from django.urls import re_path
from feeds.consumers import AlertConsumer, MapConsumer

websocket_urlpatterns = [
    re_path(r'ws/alerts/(?P<event_id>[^/]+)/$', AlertConsumer.as_asgi()),
    re_path(r'ws/map/(?P<event_id>[^/]+)/$', MapConsumer.as_asgi()),
]
