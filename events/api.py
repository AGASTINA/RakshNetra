from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Event
from .serializers import EventSerializer
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        return Event.objects.all().order_by('-start_time')
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def upload_detected_video(self, request):
        """
        Upload a detected/processed video file with detection results
        
        Request format:
        - video_file: The video file (multipart)
        - event_name: Event name (optional, defaults to detection timestamp)
        - location: Location name (optional)
        - threat_level: Threat level - 'low', 'medium', 'high' (optional, defaults to 'medium')
        - report_json: Detection report JSON (optional)
        """
        try:
            video_file = request.FILES.get('video_file')
            if not video_file:
                return Response(
                    {'error': 'No video file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get metadata
            event_name = request.data.get('event_name', f'Detected Video {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
            location = request.data.get('location', 'Unknown Location')
            threat_level = request.data.get('threat_level', Event.THREAT_MEDIUM)
            report_json = request.data.get('report_json', None)
            
            # Validate threat level
            if threat_level not in [Event.THREAT_LOW, Event.THREAT_MEDIUM, Event.THREAT_HIGH]:
                threat_level = Event.THREAT_MEDIUM
            
            # Parse report if provided
            detection_report = None
            if report_json:
                try:
                    detection_report = json.loads(report_json) if isinstance(report_json, str) else report_json
                except:
                    detection_report = None
            
            # Get or create default system user
            from accounts.models import User
            system_user, _ = User.objects.get_or_create(
                username='system',
                defaults={'email': 'system@rakshnetra.local', 'is_staff': True}
            )
            
            # Create event
            event = Event.objects.create(
                name=event_name,
                start_time=timezone.now(),
                end_time=timezone.now(),
                location=location,
                threat_level=threat_level,
                video_file=video_file,
                detection_report=detection_report,
                created_by=system_user,
                description=f'Video Detection Event - {video_file.name}'
            )
            
            serializer = EventSerializer(event)
            return Response({
                'status': 'success',
                'message': f'Video uploaded and event created: {event_name}',
                'event': serializer.data,
                'video_url': event.video_file.url if event.video_file else None,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def video_stream(self, request, pk=None):
        """Stream video file with range request support"""
        event = self.get_object()
        if not event.video_file:
            return Response(
                {'error': 'No video file associated with this event'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'video_url': event.video_file.url,
            'file_name': os.path.basename(event.video_file.name),
            'file_size': event.video_file.size,
        })
