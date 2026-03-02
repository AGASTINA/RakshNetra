from django.contrib import admin
from .models import MapLayout, MapObject, SuspectPosition

@admin.register(MapLayout)
class MapLayoutAdmin(admin.ModelAdmin):
    list_display = ('event', 'width_meters', 'height_meters')

@admin.register(MapObject)
class MapObjectAdmin(admin.ModelAdmin):
    list_display = ('map_layout', 'obj_type', 'label')

@admin.register(SuspectPosition)
class SuspectPositionAdmin(admin.ModelAdmin):
    list_display = ('event', 'timestamp', 'camera')
