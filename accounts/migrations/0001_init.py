# Lightweight compatibility migration to resolve manual migration edits
from django.db import migrations


class Migration(migrations.Migration):

    # Ensure this migration runs after the main 0001_initial migration
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = []
