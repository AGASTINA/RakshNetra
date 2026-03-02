from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import os
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from feeds.models import CameraFeed, Alert
from ai.models import AIModel, FaceIdentity
from events.models import Event

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def camera_management(request):
    """Manage camera feeds"""
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'add':
            # Add new camera
            name = request.POST.get('name', '').strip()
            protocol = request.POST.get('protocol', '')
            source = request.POST.get('source', '').strip()
            mode = request.POST.get('mode', CameraFeed.MODE_PREVIEW)
            enabled = True  # Initialize enabled flag
            
            if not all([name, protocol]) or (protocol != CameraFeed.PROTO_FILE and not source):
                messages.error(request, "Please fill all required fields")
                return render(request, 'management/cameras.html', {
                    'cameras': CameraFeed.objects.all(),
                    'protocols': CameraFeed.PROTOCOL_CHOICES,
                    'modes': CameraFeed.MODE_CHOICES,
                    'models': AIModel.objects.all(),
                })
            
            # If protocol is a file, accept uploaded file and save it
            if protocol == CameraFeed.PROTO_FILE:
                uploaded = request.FILES.get('video_file')
                if uploaded:
                    videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
                    os.makedirs(videos_dir, exist_ok=True)
                    save_path = os.path.join('videos', uploaded.name)
                    # Save using default storage (will place under MEDIA_ROOT)
                    default_storage.save(save_path, uploaded)
                    # Use absolute path for OpenCV
                    source = os.path.join(settings.MEDIA_ROOT, save_path).replace('\\', '/')
                    enabled = True
                else:
                    messages.error(request, "Please upload a video file for file protocol")
                    return redirect('camera_management')

            camera = CameraFeed.objects.create(
                name=name,
                protocol=protocol,
                source=source,
                mode=mode,
                enabled=enabled
            )
            
            # Assign models if provided
            model_ids = request.POST.getlist('models')
            if model_ids:
                camera.assigned_models.set(model_ids)
            
            messages.success(request, f"Camera '{name}' added successfully")
            return redirect('camera_management')
        
        elif action == 'edit':
            camera_id = request.POST.get('camera_id')
            camera = get_object_or_404(CameraFeed, id=camera_id)
            
            camera.name = request.POST.get('name', camera.name).strip()
            camera.protocol = request.POST.get('protocol', camera.protocol)
            # If editing and protocol is file, accept uploaded file
            new_source = request.POST.get('source', camera.source).strip()
            if camera.protocol == CameraFeed.PROTO_FILE:
                uploaded = request.FILES.get('video_file')
                if uploaded:
                    videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
                    os.makedirs(videos_dir, exist_ok=True)
                    save_path = os.path.join('videos', uploaded.name)
                    default_storage.save(save_path, uploaded)
                    new_source = os.path.join(settings.MEDIA_ROOT, save_path).replace('\\', '/')

            if camera.protocol != CameraFeed.PROTO_FILE and not new_source:
                messages.error(request, "Source is required for this protocol")
                return redirect('camera_management')

            camera.source = new_source
            camera.mode = request.POST.get('mode', camera.mode)
            camera.save()
            
            # Update models
            model_ids = request.POST.getlist('models')
            camera.assigned_models.set(model_ids)
            
            messages.success(request, f"Camera '{camera.name}' updated successfully")
            return redirect('camera_management')
        
        elif action == 'delete':
            camera_id = request.POST.get('camera_id')
            camera = get_object_or_404(CameraFeed, id=camera_id)
            camera_name = camera.name
            camera.delete()
            messages.success(request, f"Camera '{camera_name}' deleted successfully")
            return redirect('camera_management')
        
        elif action == 'toggle':
            camera_id = request.POST.get('camera_id')
            camera = get_object_or_404(CameraFeed, id=camera_id)
            camera.enabled = not camera.enabled
            camera.save()
            status = "enabled" if camera.enabled else "disabled"
            messages.success(request, f"Camera '{camera.name}' {status}")
            return redirect('camera_management')
    
    cameras = CameraFeed.objects.all()
    models = AIModel.objects.all()
    
    return render(request, 'management/cameras.html', {
        'cameras': cameras,
        'protocols': CameraFeed.PROTOCOL_CHOICES,
        'modes': CameraFeed.MODE_CHOICES,
        'models': models,
    })

@login_required(login_url='login')
def model_management(request):
    """Manage AI models"""
    # Support model actions via POST (multipart/form-data)
    if request.method == 'POST':
        action = request.POST.get('action', '').strip().lower()

        if action == 'toggle':
            model_id = request.POST.get('model_id')
            model = get_object_or_404(AIModel, id=model_id)
            model.is_active = not model.is_active
            model.save(update_fields=['is_active'])
            status = 'activated' if model.is_active else 'deactivated'
            messages.success(request, f"Model '{model.name}' {status}")
            return redirect('model_management')

        if action == 'delete':
            model_id = request.POST.get('model_id')
            model = get_object_or_404(AIModel, id=model_id)
            name = model.name
            try:
                if model.model_file and default_storage.exists(model.model_file.name):
                    default_storage.delete(model.model_file.name)
            except Exception:
                pass
            model.delete()
            messages.success(request, f"Model '{name}' deleted successfully")
            return redirect('model_management')

        if action == 'edit':
            model_id = request.POST.get('model_id')
            model = get_object_or_404(AIModel, id=model_id)
            name = request.POST.get('name', model.name).strip()
            model_type = request.POST.get('model_type', model.model_type)
            confidence_threshold = request.POST.get('confidence_threshold', model.confidence_threshold)
            description = request.POST.get('description', model.description).strip()
            model_file = request.FILES.get('model_file')

            try:
                confidence_threshold = float(confidence_threshold)
            except ValueError:
                confidence_threshold = model.confidence_threshold

            model.name = name or model.name
            model.model_type = model_type or model.model_type
            model.confidence_threshold = confidence_threshold
            model.description = description

            if model_file:
                try:
                    if model.model_file and default_storage.exists(model.model_file.name):
                        default_storage.delete(model.model_file.name)
                except Exception:
                    pass
                model.model_file.save(model_file.name, model_file)

            model.save()
            messages.success(request, f"Model '{model.name}' updated successfully")
            return redirect('model_management')

        # Upload new model (default POST action)
        name = request.POST.get('name', '').strip()
        model_type = request.POST.get('model_type', '')
        confidence_threshold = request.POST.get('confidence_threshold', '0.5')
        description = request.POST.get('description', '').strip()
        model_file = request.FILES.get('model_file')

        if not name or not model_type:
            messages.error(request, 'Please provide a name and model type')
            return redirect('model_management')

        try:
            confidence_threshold = float(confidence_threshold)
        except ValueError:
            confidence_threshold = 0.5

        model = AIModel.objects.create(
            name=name,
            model_type=model_type,
            is_active=False,
            confidence_threshold=confidence_threshold,
            description=description
        )

        if model_file:
            model.model_file.save(model_file.name, model_file)
            model.save()

        messages.success(request, f"Model '{name}' uploaded successfully")
        return redirect('model_management')

    models = AIModel.objects.all()
    return render(request, 'management/models.html', {
        'models': models,
        'model_types': AIModel.TYPE_CHOICES,
    })

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def alerts_management(request):
    """View and manage alerts"""
    alerts = Alert.objects.all().order_by('-timestamp')[:100]
    
    # Filter by severity
    severity = request.GET.get('severity')
    if severity:
        alerts = alerts.filter(severity=severity)
    
    # Filter by camera
    camera_id = request.GET.get('camera_id')
    if camera_id:
        alerts = alerts.filter(camera_id=camera_id)
    
    return render(request, 'management/alerts.html', {
        'alerts': alerts,
        'cameras': CameraFeed.objects.all(),
        'severity_choices': Alert.SEVERITY_CHOICES,
        'current_severity': severity,
        'current_camera': camera_id,
    })

@login_required(login_url='login')
def events_management(request):
    """View and manage events"""
    if request.method == 'POST':
        # Create new event
        name = request.POST.get('name')
        location = request.POST.get('location')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        threat_level = request.POST.get('threat_level', 'low')
        description = request.POST.get('description', '')
        
        if name and location and start_time and end_time:
            try:
                event = Event.objects.create(
                    name=name,
                    location=location,
                    start_time=start_time,
                    end_time=end_time,
                    threat_level=threat_level,
                    description=description,
                    created_by=request.user,
                )
                # Redirect to avoid re-submission
                from django.shortcuts import redirect
                return redirect('events_management')
            except Exception as e:
                pass  # Let template show existing events; form errors will be visible
    
    events = Event.objects.all().order_by('-start_time')
    return render(request, 'management/events.html', {
        'events': events,
        'threat_levels': Event.THREAT_CHOICES,
    })

@login_required(login_url='login')
def face_management(request):
    """Manage face identities for recognition"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            face_id = request.POST.get('face_id')
            face = get_object_or_404(FaceIdentity, id=face_id)
            try:
                # delete image file from storage
                if face.face_image and default_storage.exists(face.face_image.name):
                    default_storage.delete(face.face_image.name)
            except Exception:
                pass
            face.delete()
            messages.success(request, f"Face identity deleted successfully")
            return redirect('face_management')

        # Otherwise treat as upload
        label = request.POST.get('label', '').strip()
        identity_type = request.POST.get('identity_type', 'unknown')
        face_image = request.FILES.get('face_image')
        position = request.POST.get('position', '').strip()
        description = request.POST.get('description', '').strip()
        metadata = request.POST.get('metadata', '')
        
        if not label or not face_image:
            messages.error(request, 'Please provide a label and image')
            return redirect('face_management')
        
        try:
            metadata_payload = {}
            if metadata:
                metadata_payload['notes'] = metadata

            face = FaceIdentity.objects.create(
                label=label,
                identity_type=identity_type,
                position=position,
                description=description,
                metadata=metadata_payload
            )
            face.face_image.save(face_image.name, face_image)
            face.save()
            messages.success(request, f"Face identity '{label}' uploaded successfully")
        except Exception as e:
            messages.error(request, f"Error uploading face: {str(e)}")
        
        return redirect('face_management')
    
    faces = FaceIdentity.objects.all()
    return render(request, 'management/faces.html', {
        'faces': faces,
        'identity_types': FaceIdentity.IDENTITY_CHOICES,
    })
