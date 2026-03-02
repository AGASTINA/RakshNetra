from django.db import models

def face_identity_upload_path(instance, filename):
    identity_folder = instance.identity_type or 'unknown'
    safe_folder = identity_folder.replace(' ', '_').lower()
    return f"face_identities/{safe_folder}/{filename}"

class AIModel(models.Model):
    TYPE_WEAPON = 'weapon_detection'
    TYPE_FIRE = 'fire_smoke'
    TYPE_BEHAVIOR = 'suspicious_behavior'
    TYPE_VEHICLE = 'vehicle_detection'
    TYPE_TRACKING = 'person_tracking'
    TYPE_FACE = 'face_recognition'
    TYPE_NSG_CLASS = 'nsg_classification'
    TYPE_FIGHTING = 'fighting_violence_detection'

    TYPE_CHOICES = [
        (TYPE_WEAPON, 'Weapon Detection'),
        (TYPE_FIRE, 'Fire / Smoke Detection'),
        (TYPE_BEHAVIOR, 'Suspicious Behavior'),
        (TYPE_VEHICLE, 'Vehicle Detection'),
        (TYPE_TRACKING, 'Person Tracking'),
        (TYPE_FACE, 'Face Recognition'),
        (TYPE_NSG_CLASS, 'NSG vs Non-NSG Classification'),
        (TYPE_FIGHTING, 'Fighting / Violence Detection'),
    ]

    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    model_file = models.FileField(upload_to='models/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    confidence_threshold = models.FloatField(default=0.5)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.model_type})"

class ModelActivationRule(models.Model):
    """Auto-activation logic: Motion -> Person, Person+Posture -> Weapon, etc."""
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    trigger = models.CharField(max_length=100)  # e.g., 'motion', 'person_detected', 'posture_change'
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.model.name} triggered by {self.trigger}"

class FaceIdentity(models.Model):
    IDENTITY_NSG = 'nsg'
    IDENTITY_POLICE = 'police'
    IDENTITY_VIP = 'vip'
    IDENTITY_SUSPECT = 'suspect'
    IDENTITY_UNKNOWN = 'unknown'

    IDENTITY_CHOICES = [
        (IDENTITY_NSG, 'NSG Personnel'),
        (IDENTITY_POLICE, 'Police Personnel'),
        (IDENTITY_VIP, 'VIP'),
        (IDENTITY_SUSPECT, 'Known Suspect'),
        (IDENTITY_UNKNOWN, 'Unknown'),
    ]

    label = models.CharField(max_length=100)
    identity_type = models.CharField(max_length=20, choices=IDENTITY_CHOICES)
    face_image = models.ImageField(upload_to=face_identity_upload_path)
    position = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.label} ({self.identity_type})"
