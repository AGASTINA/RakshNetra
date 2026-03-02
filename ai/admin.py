from django.contrib import admin
from .models import AIModel, ModelActivationRule, FaceIdentity

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'is_active', 'confidence_threshold')
    list_filter = ('model_type', 'is_active')

@admin.register(ModelActivationRule)
class ModelActivationRuleAdmin(admin.ModelAdmin):
    list_display = ('model', 'trigger', 'enabled')

@admin.register(FaceIdentity)
class FaceIdentityAdmin(admin.ModelAdmin):
    list_display = ('label', 'identity_type')
