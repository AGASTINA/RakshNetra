from django.urls import path
from situational_map.views import map_management, situational_map_page

urlpatterns = [
    path('situational-map/', situational_map_page, name='situational_map'),
    path('manage/map/', map_management, name='map_management'),
]
