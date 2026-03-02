from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from ai.models import AIModel, ModelActivationRule, FaceIdentity
from ai.serializers import AIModelSerializer, ModelActivationRuleSerializer, FaceIdentitySerializer
from django.core.files.storage import default_storage
import os

class AIModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing AI models.
    Supports model upload, activation, and configuration.
    """
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """List all available model types"""
        types = [
            {'value': t[0], 'label': t[1]}
            for t in AIModel.TYPE_CHOICES
        ]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active models"""
        active_models = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(active_models, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activate/deactivate a model"""
        model = self.get_object()
        model.is_active = not model.is_active
        model.save()
        return Response({
            'status': 'success',
            'is_active': model.is_active,
            'model_name': model.name
        })
    
    @action(detail=True, methods=['post'])
    def update_threshold(self, request, pk=None):
        """Update confidence threshold for a model"""
        model = self.get_object()
        threshold = request.data.get('confidence_threshold')
        
        if threshold is None:
            return Response(
                {'error': 'confidence_threshold is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            threshold = float(threshold)
            if not 0 <= threshold <= 1:
                return Response(
                    {'error': 'confidence_threshold must be between 0 and 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.confidence_threshold = threshold
            model.save()
            return Response({
                'status': 'success',
                'confidence_threshold': model.confidence_threshold
            })
        except ValueError:
            return Response(
                {'error': 'Invalid threshold value'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def add_activation_rule(self, request, pk=None):
        """Add an activation trigger rule to a model"""
        model = self.get_object()
        trigger = request.data.get('trigger')
        enabled = request.data.get('enabled', True)
        
        if not trigger:
            return Response(
                {'error': 'trigger is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rule, created = ModelActivationRule.objects.get_or_create(
            model=model,
            trigger=trigger,
            defaults={'enabled': enabled}
        )
        
        serializer = ModelActivationRuleSerializer(rule)
        return Response({
            'status': 'created' if created else 'already_exists',
            'rule': serializer.data
        })

class FaceIdentityViewSet(viewsets.ModelViewSet):
    """API endpoint for managing face identity database"""
    queryset = FaceIdentity.objects.all()
    serializer_class = FaceIdentitySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """List identity types"""
        types = [
            {'value': t[0], 'label': t[1]}
            for t in FaceIdentity.IDENTITY_CHOICES
        ]
        return Response(types)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Filter identities by type"""
        identity_type = request.query_params.get('type')
        if not identity_type:
            return Response(
                {'error': 'type parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        identities = self.queryset.filter(identity_type=identity_type)
        serializer = self.get_serializer(identities, many=True)
        return Response(serializer.data)
