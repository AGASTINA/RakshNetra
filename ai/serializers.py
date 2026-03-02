from rest_framework import serializers
from ai.models import AIModel, ModelActivationRule, FaceIdentity

class ModelActivationRuleSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = ModelActivationRule
        fields = ['id', 'model', 'model_name', 'trigger', 'enabled']

class AIModelSerializer(serializers.ModelSerializer):
    activation_rules = ModelActivationRuleSerializer(
        source='modelactivationrule_set',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'model_type', 'model_file', 'is_active',
            'confidence_threshold', 'description', 'metadata', 'activation_rules'
        ]
        read_only_fields = ['id']

class FaceIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceIdentity
        fields = ['id', 'label', 'identity_type', 'face_image', 'position', 'description', 'metadata']
        read_only_fields = ['id']
