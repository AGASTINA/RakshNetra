from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from feeds.models import CameraFeed, Alert
from feeds.serializers import CameraFeedSerializer, AlertSerializer
from feeds.video import camera_current_detections, _latest_face_detections

class CameraFeedViewSet(ModelViewSet):
    """
    API endpoint for managing camera feeds.
    Supports all CRUD operations and protocol configuration.
    """
    queryset = CameraFeed.objects.all()
    serializer_class = CameraFeedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def protocols(self, request):
        """List available camera protocols"""
        protocols = [
            {'value': proto[0], 'label': proto[1]}
            for proto in CameraFeed.PROTOCOL_CHOICES
        ]
        return Response(protocols)
    
    @action(detail=False, methods=['get'])
    def modes(self, request):
        """List available stream modes"""
        modes = [
            {'value': mode[0], 'label': mode[1]}
            for mode in CameraFeed.MODE_CHOICES
        ]
        return Response(modes)
    
    @action(detail=True, methods=['post'])
    def assign_models(self, request, pk=None):
        """Assign AI models to a camera"""
        camera = self.get_object()
        model_ids = request.data.get('model_ids', [])
        
        try:
            from ai.models import AIModel
            models = AIModel.objects.filter(id__in=model_ids)
            camera.assigned_models.set(models)
            return Response({
                'status': 'success',
                'message': f'Assigned {len(models)} models to {camera.name}',
                'assigned_models': AIModelSerializer(models, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def toggle_enabled(self, request, pk=None):
        """Enable/disable a camera"""
        camera = self.get_object()
        camera.enabled = not camera.enabled
        camera.save()
        return Response({
            'status': 'success',
            'enabled': camera.enabled
        })
    
    @action(detail=True, methods=['get'])
    def current_detections(self, request, pk=None):
        """Get current detections from camera"""
        camera = self.get_object()
        
        # Get detections from global cache
        detections = {
            'camera_id': camera.id,
            'camera_name': camera.name,
            'faces': [],
            'objects': [],
            'weapons': [],
            'timestamp': None
        }
        
        # Get current frame detections
        if camera.id in camera_current_detections:
            detections.update(camera_current_detections[camera.id])
            detections['timestamp'] = str(__import__('datetime').datetime.now())
        
        # Get latest face detections and reformat for API
        if camera.id in _latest_face_detections:
            face_data = _latest_face_detections[camera.id]
            raw_faces = face_data.get('faces', [])
            formatted_faces = []
            for face in raw_faces:
                formatted_faces.append({
                    'name': face.get('label', 'Unknown'),
                    'title': face.get('position', ''),
                    'confidence': face.get('confidence', 0.0),
                    'identity_type': face.get('identity_type', '')
                })
            detections['faces'] = formatted_faces
        
        return Response(detections)

class AlertViewSet(ModelViewSet):
    """API endpoint for managing alerts and threats"""
    queryset = Alert.objects.all().order_by('-timestamp')
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def severities(self, request):
        """List alert severity levels"""
        severities = [
            {'value': sev[0], 'label': sev[1]}
            for sev in Alert.SEVERITY_CHOICES
        ]
        return Response(severities)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get only critical alerts"""
        alerts = self.queryset.filter(severity=Alert.SEVERITY_CRITICAL)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent alerts (last 24 hours)"""
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(hours=24)
        alerts = self.queryset.filter(timestamp__gte=since)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

from feeds.serializers import AIModelSerializer
