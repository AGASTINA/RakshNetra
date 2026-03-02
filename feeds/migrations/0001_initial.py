from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ai', '0001_initial'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CameraFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('protocol', models.CharField(choices=[('webcam', 'USB Webcam'), ('rtsp', 'RTSP (IP Camera/CCTV)'), ('rtmp', 'RTMP'), ('http', 'HTTP/HTTPS'), ('hls', 'HLS (m3u8)'), ('file', 'Video File')], max_length=20)),
                ('source', models.CharField(help_text='URL, file path, device index, etc.', max_length=500)),
                ('mode', models.CharField(choices=[('preview', 'Preview Mode (Browser)'), ('ai', 'AI Mode (OpenCV)')], default='preview', max_length=20)),
                ('enabled', models.BooleanField(default=True)),
                ('assigned_models', models.ManyToManyField(blank=True, to='ai.aimodel')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threat_type', models.CharField(max_length=100)),
                ('severity', models.CharField(choices=[('info', 'INFO'), ('warning', 'WARNING'), ('critical', 'CRITICAL')], default='warning', max_length=20)),
                ('confidence', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('snapshot', models.ImageField(blank=True, null=True, upload_to='alert_snapshots/')),
                ('location', models.CharField(blank=True, max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('camera', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='feeds.camerafeed')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
    ]
