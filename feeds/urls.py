from django.urls import path
from .video import VideoFeedView, DashboardView, CameraViewerView, latest_face_info
from .management_views import (
    camera_management, model_management, 
    alerts_management, events_management, face_management
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('manage/cameras/', camera_management, name='camera_management'),
    path('manage/models/', model_management, name='model_management'),
    path('manage/alerts/', alerts_management, name='alerts_management'),
    path('manage/events/', events_management, name='events_management'),
    path('manage/faces/', face_management, name='face_management'),
    path('camera/<int:camera_id>/', CameraViewerView.as_view(), name='camera_viewer'),
    path('video_feed/<int:camera_id>/', VideoFeedView.as_view(), name='video_feed'),
    path('camera/<int:camera_id>/faces/', latest_face_info, name='camera_face_info'),
]
