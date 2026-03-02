from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/events/', include('events.api_urls')),
    path('api/ai/', include('ai.api_urls')),
    path('api/map/', include('situational_map.api_urls')),
    path('', include('situational_map.urls')),
    path('', include('feeds.api_urls')),
    path('', include('feeds.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
