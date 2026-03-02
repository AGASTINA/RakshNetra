import cv2
import os
import threading
import logging
import time
import shutil
import subprocess
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import CameraFeed, Alert
from events.models import Event
from ai.models import AIModel
from ai.inference import ModelInferenceEngine, FrameProcessor

logger = logging.getLogger(__name__)

class FrameBuffer:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()

    def set_frame(self, frame):
        with self.lock:
            self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame

frame_buffers = {}
last_alert_times = {}
_repaired_video_cache = {}
_repair_attempted = set()
_latest_face_detections = {}
_latest_face_lock = threading.Lock()
last_detections = {}  # Global detection cache for all cameras
camera_current_detections = {}  # Store all detections for current frame


def _update_latest_faces(camera_id, detections):
    if not detections:
        return
    faces = []
    for det in detections:
        label = det.get('label')
        identity_type = det.get('identity_type')
        position = det.get('position')
        confidence = float(det.get('confidence', 0.0))
        if not label:
            continue
        faces.append({
            'label': label,
            'identity_type': identity_type,
            'position': position,
            'confidence': confidence,
        })
    if not faces:
        return
    faces.sort(key=lambda item: item.get('confidence', 0.0), reverse=True)
    with _latest_face_lock:
        _latest_face_detections[camera_id] = {
            'timestamp': time.time(),
            'faces': faces[:10]
        }


def _try_repair_mp4(source_path):
    if not source_path or not source_path.lower().endswith('.mp4'):
        return source_path

    if source_path in _repaired_video_cache:
        return _repaired_video_cache[source_path]

    if source_path in _repair_attempted:
        return source_path

    _repair_attempted.add(source_path)
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        logger.warning("ffmpeg not found; cannot repair mp4 for %s", source_path)
        return source_path

    try:
        fixed_path = source_path.replace('.mp4', '_fixed.mp4')
        result = subprocess.run(
            [ffmpeg_path, '-y', '-i', source_path, '-c', 'copy', '-movflags', '+faststart', fixed_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        if result.returncode == 0 and os.path.exists(fixed_path):
            _repaired_video_cache[source_path] = fixed_path
            logger.info("Repaired mp4 saved to %s", fixed_path)
            return fixed_path
    except Exception as e:
        logger.error("Failed to repair mp4 %s: %s", source_path, e)

    return source_path

def get_frame_buffer(camera_id):
    if camera_id not in frame_buffers:
        frame_buffers[camera_id] = FrameBuffer()
    return frame_buffers[camera_id]

def _open_capture(camera):
    source = camera.source
    if camera.protocol == CameraFeed.PROTO_WEBCAM:
        idx = int(source) if str(source).isdigit() else 0
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    else:
        if camera.protocol == CameraFeed.PROTO_FILE:
            source = _try_repair_mp4(source)
        cap = cv2.VideoCapture(source)

    if cap is not None and cap.isOpened():
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
    return cap


def generate_mjpeg(camera_id):
    """MJPEG frame generator with OpenCV and AI inference"""
    try:
        camera = CameraFeed.objects.get(id=camera_id)
        if not camera.enabled:
            raise ValueError(f"Camera {camera_id} is disabled")
        buffer = get_frame_buffer(camera_id)
        cap = _open_capture(camera)

        if not cap or not cap.isOpened():
            raise ValueError(f"Cannot open source: {camera.source}")

        # Load assigned models (active only). If none assigned, use globally active models.
        assigned_models = camera.assigned_models.all()
        if assigned_models.exists():
            active_models = assigned_models.filter(is_active=True)
        else:
            active_models = AIModel.objects.filter(is_active=True)
        
        loaded_models = {}
        
        # Always include face recognition
        loaded_models['face_recognition'] = {
            'model': None,
            'type': AIModel.TYPE_FACE,
            'threshold': 0.55,
            'name': 'Face Identity'
        }
        
        for model in active_models:
            if model.model_type == AIModel.TYPE_FACE and not model.model_file:
                loaded_models[model.id] = {
                    'model': None,
                    'type': model.model_type,
                    'threshold': model.confidence_threshold,
                    'name': model.name
                }
                continue
            if model.model_file:
                try:
                    loaded_model = ModelInferenceEngine.load_model(
                        model.model_file.path,
                        model.model_type
                    )
                    if loaded_model:
                        loaded_models[model.id] = {
                            'model': loaded_model,
                            'type': model.model_type,
                            'threshold': model.confidence_threshold,
                            'name': model.name
                        }
                except Exception as e:
                    logger.error(f"Failed to load model {model.name}: {e}")

        frame_count = 0
        fail_count = 0
        frame_skip = 3  # Process every 3rd frame for video files
        local_last_detections = {}
        
        while True:
            if frame_count % 30 == 0:
                try:
                    camera.refresh_from_db(fields=['enabled'])
                    if not camera.enabled:
                        logger.info("Camera %s disabled; stopping stream", camera_id)
                        break
                except Exception:
                    pass
            if not cap or not cap.isOpened():
                cap = _open_capture(camera)
                time.sleep(0.2)
                continue

            ret, frame = cap.read()
            if not ret:
                fail_count += 1
                if fail_count >= 5:
                    logger.warning("Reopening camera %s after read failures", camera_id)
                    try:
                        cap.release()
                    except Exception:
                        pass
                    cap = _open_capture(camera)
                    fail_count = 0
                time.sleep(0.05)
                last_frame = buffer.get_frame()
                if last_frame is not None:
                    _, buffer_frame = cv2.imencode('.jpg', last_frame)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n'
                           b'Content-Length: ' + str(len(buffer_frame)).encode() + b'\r\n\r\n'
                           + buffer_frame.tobytes() + b'\r\n')
                continue

            fail_count = 0

            annotated_frame = frame.copy()
            inference_frame = frame
            
            # Resize for faster inference (optimize for speed)
            if getattr(settings, 'INFERENCE_RESIZE', None):
                try:
                    inference_frame = cv2.resize(frame, settings.INFERENCE_RESIZE, interpolation=cv2.INTER_LINEAR)
                except Exception:
                    inference_frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)
            else:
                # Default faster resolution
                inference_frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)

            # Run inference only on key frames to boost speed
            should_infer = (frame_count % frame_skip == 0) or camera.protocol == CameraFeed.PROTO_WEBCAM
            
            if should_infer and camera.mode == CameraFeed.MODE_AI:
                frame_detections = {'faces': [], 'objects': [], 'weapons': [], 'fighting': []}
                all_detections = []  # Collect all detections for fighting detection
                
                for model_id, model_info in loaded_models.items():
                    try:
                        result = ModelInferenceEngine.run_inference(
                            model_info['model'],
                            inference_frame,
                            model_info['type'],
                            model_info['threshold'],
                            source_shape=getattr(annotated_frame, "shape", None)
                        )
                        if result.get('detections'):
                            detections = result['detections']
                            
                            # Filter NSG classification: only show NSG personnel, hide non-NSG
                            if model_info['type'] == AIModel.TYPE_NSG_CLASS:
                                detections = [
                                    d for d in detections 
                                    if 'nsg' in str(d.get('label', '')).lower() and 
                                       'non' not in str(d.get('label', '')).lower()
                                ]
                                # Skip if no NSG detections
                                if not detections:
                                    continue
                            
                            local_last_detections[model_id] = detections
                            all_detections.extend(detections)
                            annotated_frame = FrameProcessor.draw_detections(
                                annotated_frame,
                                detections
                            )
                            if model_info['type'] == AIModel.TYPE_FACE:
                                _update_latest_faces(camera_id, detections)
                                # Store faces for dashboard
                                for det in detections:
                                    frame_detections['faces'].append({
                                        'name': det.get('label', 'Unknown'),
                                        'title': det.get('description', ''),
                                        'confidence': det.get('confidence', 0)
                                    })
                            else:
                                frame_detections['objects'].append({
                                    'type': model_info['name'],
                                    'count': len(detections)
                                })
                            logger.debug(f"Model {model_info['name']}: {len(detections)} detections")
                            _maybe_create_alert(camera, model_id, model_info, {'detections': detections})
                    except Exception as e:
                        logger.error(f"Inference error for model {model_id}: {e}")
                
                # Detect fighting based on multiple people interactions
                try:
                    fighting_detections = FrameProcessor.detect_fighting(all_detections, annotated_frame.shape)
                    if fighting_detections:
                        # Draw fighting detections with red boxes
                        annotated_frame = FrameProcessor.draw_detections(annotated_frame, fighting_detections)
                        frame_detections['fighting'] = [{
                            'people_count': det.get('people_count', 2),
                            'confidence': det.get('confidence', 0.8)
                        } for det in fighting_detections]
                        # Create alert for fighting
                        if fighting_detections:
                            _maybe_create_alert(camera, 'fighting_detection', 
                                              {'name': 'Fighting Detection', 'type': AIModel.TYPE_FIGHTING}, 
                                              {'detections': fighting_detections})
                except Exception as e:
                    logger.error(f"Fighting detection error: {e}")
                
                # Store in global cache
                camera_current_detections[camera_id] = frame_detections
            else:
                # Reuse last detections on skipped frames
                for model_id, detections in local_last_detections.items():
                    if detections:
                        try:
                            annotated_frame = FrameProcessor.draw_detections(
                                annotated_frame,
                                detections
                            )
                        except Exception:
                            pass

            buffer.set_frame(annotated_frame)

            # Encode frame as JPEG
            _, buffer_frame = cv2.imencode('.jpg', annotated_frame)
            frame_count += 1
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(buffer_frame)).encode() + b'\r\n\r\n'
                   + buffer_frame.tobytes() + b'\r\n')

        try:
            cap.release()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error streaming camera {camera_id}: {e}")


def _maybe_create_alert(camera, model_id, model_info, result):
    detections = result.get('detections') or []
    if not detections:
        return

    # Auto-activate only for configured model types (others respect manual disable)
    auto_types = set(getattr(settings, 'MODEL_AUTO_ACTIVATE_TYPES', []))
    if model_info.get('type') in auto_types:
        try:
            model = AIModel.objects.get(id=model_id)
            if not model.is_active:
                model.is_active = True
                model.save(update_fields=['is_active'])
        except Exception:
            pass

    # Alert throttling per camera+model
    now = time.time()
    key = (camera.id, model_id)
    last_time = last_alert_times.get(key, 0)
    if now - last_time < 5:
        return
    last_alert_times[key] = now

    severity_map = {
        AIModel.TYPE_WEAPON: Alert.SEVERITY_CRITICAL,
        AIModel.TYPE_FIRE: Alert.SEVERITY_WARNING,
        AIModel.TYPE_BEHAVIOR: Alert.SEVERITY_WARNING,
        AIModel.TYPE_VEHICLE: Alert.SEVERITY_INFO,
        AIModel.TYPE_TRACKING: Alert.SEVERITY_INFO,
        AIModel.TYPE_FACE: Alert.SEVERITY_INFO,
        AIModel.TYPE_NSG_CLASS: Alert.SEVERITY_WARNING,
    }
    severity = severity_map.get(model_info['type'], Alert.SEVERITY_WARNING)

    event = camera.event
    if event is None:
        event = Event.objects.order_by('-start_time').first()
    if event is None:
        logger.warning("No event available for alert creation")
        return

    try:
        Alert.objects.create(
            event=event,
            camera=camera,
            threat_type=model_info['type'],
            severity=severity,
            confidence=max([float(d.get('confidence', 0.0)) for d in detections]) if detections else 0.0,
            metadata={
                'model_name': model_info['name'],
                'detections': len(detections)
            }
        )
    except Exception as e:
        logger.error(f"Failed to create alert: {e}")

class VideoFeedView(View):
    def get(self, request, camera_id):
        try:
            return StreamingHttpResponse(
                generate_mjpeg(camera_id),
                content_type='multipart/x-mixed-replace; boundary=frame'
            )
        except Exception as e:
            return StreamingHttpResponse(f"Error: {e}", status=500)


@login_required(login_url='login')
def latest_face_info(request, camera_id):
    with _latest_face_lock:
        payload = _latest_face_detections.get(camera_id, {
            'timestamp': None,
            'faces': []
        })
    return JsonResponse(payload)

class CameraViewerView(LoginRequiredMixin, TemplateView):
    """Display camera viewer page with live stream"""
    template_name = 'camera_viewer.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camera_id = self.kwargs.get('camera_id')
        try:
            camera = CameraFeed.objects.get(id=camera_id)
            context['camera'] = camera
            detected_url = None
            if camera.event and getattr(camera.event, 'video_file', None):
                try:
                    detected_url = camera.event.video_file.url
                except Exception:
                    detected_url = None
            context['detected_video_url'] = detected_url
        except CameraFeed.DoesNotExist:
            context['error'] = 'Camera not found'
        return context

@method_decorator(ensure_csrf_cookie, name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        context = super().get_context_data(**kwargs)
        
        # Get data as dicts
        cameras = list(CameraFeed.objects.all().values('id', 'name', 'enabled', 'protocol', 'source'))
        events_queryset = Event.objects.all().order_by('-start_time')
        
        # Convert events to dict with explicit datetime formatting
        events = []
        for event in events_queryset:
            events.append({
                'id': event.id,
                'name': event.name,
                'location': event.location,
                'threat_level': event.threat_level,
                'start_time': event.start_time.isoformat() if event.start_time else ''
            })
        
        # Convert to JSON strings for template embedding using DjangoJSONEncoder 
        context['cameras_json'] = json.dumps(cameras, cls=DjangoJSONEncoder)
        context['events_json'] = json.dumps(events, cls=DjangoJSONEncoder)
        
        # Also pass for template loops
        context['cameras'] = cameras
        context['events'] = events
        
        active_models = AIModel.objects.filter(is_active=True)
        context['active_models'] = active_models
        context['all_models'] = AIModel.objects.all()
        context['active_models_count'] = active_models.count()
        context['total_models_count'] = AIModel.objects.count()
        return context
