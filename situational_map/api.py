from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from PIL import Image

from situational_map.models import MapLayout, MapObject
from situational_map.serializers import MapLayoutSerializer, MapObjectSerializer
from events.models import Event

class MapLayoutViewSet(viewsets.ModelViewSet):
    queryset = MapLayout.objects.select_related('event').all()
    serializer_class = MapLayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = super().get_queryset()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event')
        image = request.FILES.get('image')
        name = request.data.get('name', 'Default Map')
        width_meters = request.data.get('width_meters') or request.data.get('width', 1.0)
        height_meters = request.data.get('height_meters') or request.data.get('height', 1.0)

        if not image:
            return Response(
                {'error': 'image is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event = None
        if event_id:
            event = get_object_or_404(Event, id=event_id)

        try:
            width_meters = float(width_meters) if width_meters else 1.0
            height_meters = float(height_meters) if height_meters else 1.0
        except ValueError:
            width_meters = 1.0
            height_meters = 1.0

        image_obj = Image.open(image)
        width_pixels, height_pixels = image_obj.size

        # Check if there's an existing standalone map (no event) and update it
        if not event:
            layout = MapLayout.objects.filter(event__isnull=True).first()
            if layout:
                layout.image = image
                layout.width_pixels = width_pixels
                layout.height_pixels = height_pixels
                layout.width_meters = width_meters
                layout.height_meters = height_meters
                layout.name = name
                layout.save()
                serializer = self.get_serializer(layout)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new layout
        layout = MapLayout.objects.create(
            event=event,
            name=name,
            image=image,
            width_pixels=width_pixels,
            height_pixels=height_pixels,
            width_meters=width_meters,
            height_meters=height_meters
        )
        serializer = self.get_serializer(layout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MapObjectViewSet(viewsets.ModelViewSet):
    queryset = MapObject.objects.select_related('map_layout').all()
    serializer_class = MapObjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (JSONParser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        layout_id = self.request.query_params.get('layout')
        event_id = self.request.query_params.get('event')
        if layout_id:
            queryset = queryset.filter(map_layout_id=layout_id)
        if event_id:
            queryset = queryset.filter(map_layout__event_id=event_id)
        return queryset
