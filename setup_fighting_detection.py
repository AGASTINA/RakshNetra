import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from ai.models import AIModel

# Create fighting detection model
try:
    fighting_model, created = AIModel.objects.get_or_create(
        name='Fighting / Violence Detection',
        model_type=AIModel.TYPE_FIGHTING,
        defaults={
            'is_active': True,
            'confidence_threshold': 0.5,
            'description': 'Detects fighting and violence based on person interactions and proximity',
            'metadata': {
                'algorithm': 'interaction_clustering',
                'detection_method': 'proximity_analysis',
                'min_people': 2,
                'features': ['overlap_detection', 'distance_based', 'crowd_analysis']
            }
        }
    )
    
    if created:
        print(f"✓ Created {fighting_model.name}")
        print(f"  Type: {fighting_model.get_model_type_display()}")
        print(f"  Active: {fighting_model.is_active}")
        print(f"  Threshold: {fighting_model.confidence_threshold}")
    else:
        # Update existing
        if not fighting_model.is_active:
            fighting_model.is_active = True
            fighting_model.save()
            print(f"✓ Activated {fighting_model.name}")
        else:
            print(f"✓ {fighting_model.name} already active")
    
    # List all active models
    active_models = AIModel.objects.filter(is_active=True)
    print(f"\nActive detection models ({active_models.count()}):")
    for model in active_models:
        print(f"  • {model.name} ({model.get_model_type_display()})")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
