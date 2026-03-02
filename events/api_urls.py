from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'', api.EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
