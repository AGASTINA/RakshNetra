from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AIModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                (
                    "model_type",
                    models.CharField(
                        choices=[
                            ("weapon_detection", "Weapon Detection"),
                            ("fire_smoke", "Fire / Smoke Detection"),
                            ("suspicious_behavior", "Suspicious Behavior"),
                            ("vehicle_detection", "Vehicle Detection"),
                            ("person_tracking", "Person Tracking"),
                            ("face_recognition", "Face Recognition"),
                            ("nsg_classification", "NSG vs Non-NSG Classification"),
                        ],
                        max_length=50,
                    ),
                ),
                ("model_file", models.FileField(blank=True, null=True, upload_to="models/")),
                ("is_active", models.BooleanField(default=False)),
                ("confidence_threshold", models.FloatField(default=0.5)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="ModelActivationRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("trigger", models.CharField(max_length=100)),
                ("enabled", models.BooleanField(default=True)),
                (
                    "model",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ai.aimodel"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FaceIdentity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(max_length=100)),
                (
                    "identity_type",
                    models.CharField(
                        choices=[
                            ("nsg", "NSG Personnel"),
                            ("suspect", "Known Suspect"),
                            ("unknown", "Unknown"),
                        ],
                        max_length=20,
                    ),
                ),
                ("face_image", models.ImageField(upload_to="face_identities/")),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
        ),
    ]
