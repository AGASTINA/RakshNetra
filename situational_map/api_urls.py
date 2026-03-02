from django.urls import path, include
from rest_framework.routers import DefaultRouter
from situational_map.api import MapLayoutViewSet, MapObjectViewSet

router = DefaultRouter()
router.register(r'layouts', MapLayoutViewSet, basename='map-layout')
router.register(r'objects', MapObjectViewSet, basename='map-object')

urlpatterns = [
    path('', include(router.urls)),
]
