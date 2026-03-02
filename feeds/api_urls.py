from django.urls import path, include
from rest_framework.routers import DefaultRouter
from feeds.api import CameraFeedViewSet, AlertViewSet
from feeds.video import VideoFeedView, DashboardView

router = DefaultRouter()
router.register(r'cameras', CameraFeedViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('video_feed/<int:camera_id>/', VideoFeedView.as_view(), name='video_feed'),
]
