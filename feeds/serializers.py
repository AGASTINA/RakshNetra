from rest_framework import serializers
from feeds.models import CameraFeed, Alert
from ai.models import AIModel

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'model_type', 'is_active', 'confidence_threshold']

class CameraFeedSerializer(serializers.ModelSerializer):
    assigned_models = AIModelSerializer(many=True, read_only=True)
    assigned_model_ids = serializers.PrimaryKeyRelatedField(
        queryset=AIModel.objects.all(),
        many=True,
        write_only=True,
        source='assigned_models'
    )
    detected_video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CameraFeed
        fields = [
            'id', 'name', 'protocol', 'source', 'mode', 'enabled',
            'event', 'assigned_models', 'assigned_model_ids', 'detected_video_url'
        ]
        read_only_fields = ['id']

    def get_detected_video_url(self, obj):
        event = getattr(obj, 'event', None)
        if event and getattr(event, 'video_file', None):
            try:
                return event.video_file.url
            except Exception:
                return None
        return None

class AlertSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'event', 'camera', 'camera_name', 'threat_type',
            'severity', 'confidence', 'timestamp', 'snapshot',
            'location', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']
