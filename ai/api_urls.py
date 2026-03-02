from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ai.api import AIModelViewSet, FaceIdentityViewSet

router = DefaultRouter()
router.register(r'models', AIModelViewSet)
router.register(r'faces', FaceIdentityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
