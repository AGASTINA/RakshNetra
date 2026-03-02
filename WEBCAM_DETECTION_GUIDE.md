# RakshNetra: Webcam Detection Setup Guide

## ✓ Status
- **Webcam Support**: ✅ Enabled (Device 0 accessible)
- **Webcam Camera**: ✅ Created (ID: 2, "Webcam Feed")
- **MJPEG Stream**: ✅ Working at `/video_feed/2/`
- **AI Inference Pipeline**: ✅ Integrated into stream generator
- **Model Upload**: ✅ Ready

---

## Quick Start (5 Steps)

### 1. Start the Dev Server
```powershell
cd C:\Workspace\RakshNetra
python manage.py runserver
```
Server runs at: `http://localhost:8000`

### 2. Create a Test Account (First Time Only)
```powershell
# In another terminal:
python manage.py createsuperuser
# Or use an existing account
```

### 3. Login to the Dashboard
- Go to: `http://localhost:8000/accounts/login/`
- Enter your credentials
- You'll see the dashboard with cameras, models, and events

### 4. Upload Your .pt Model
1. Click **"+ Upload Model"** on the AI Models page (`http://localhost:8000/manage/models/`)
2. Fill in:
   - **Model Name**: e.g., "YOLOv8 Weapon Detection"
   - **Model Type**: Choose from dropdown (e.g., "Weapon Detection")
   - **Model File**: Upload your `.pt` file
   - **Confidence Threshold**: 0.5 (default is good)
3. Click **"Upload Model"**
4. Model saves to: `C:\Workspace\RakshNetra\media\models\`

### 5. Enable Detection & View Stream
1. Go to **AI Models** page
2. Click **"Activate"** on your model card
3. Go to **Camera Management** (`http://localhost:8000/manage/cameras/`)
4. Find **"Webcam Feed"** camera
5. Click **"Edit"**
6. Under "Assign AI Models", **check your model**
7. Click **"Save Camera"**
8. Click **"👁 View Live"** to watch detection stream

---

## File Upload Locations

| Type | Upload URL | Files Save To |
|------|-----------|---------------|
| **AI Models (.pt, .onnx, .pb)** | `http://localhost:8000/manage/models/` | `media/models/` |
| **Video Files (for file-based cameras)** | `http://localhost:8000/manage/cameras/` | `media/videos/` |
| **Face Images** | `http://localhost:8000/manage/faces/` | `media/face_identities/` |

---

## Webcam Detection Workflow

```
┌─────────────────────────────────┐
│  Webcam (Device 0)              │
└────────────┬────────────────────┘
             │
             ├─→ OpenCV Capture (30fps)
             │
             ├─→ Load Active Models
             │   ├─ Model 1 (Weapon Detection)
             │   ├─ Model 2 (Person Tracking)
             │   └─ ...
             │
             ├─→ Run Inference
             │   ├─ Draw Bounding Boxes
             │   ├─ Add Confidence Scores
             │   └─ ...
             │
             ├─→ Encode Frame as JPEG
             │
             └─→ Stream as MJPEG
                 (multipart/x-mixed-replace)
```

### How It Works:
1. **Camera Stream**: Reads from webcam device 0 (or any configured source)
2. **Model Loading**: Loads all active models assigned to the camera
3. **Inference**: Runs each model on every frame
4. **Drawing**: Overlays detection boxes and labels on frame
5. **Streaming**: Sends MJPEG stream to browser via `/video_feed/<camera_id>/`

---

## API Endpoints

### Video Stream
- **Endpoint**: `/video_feed/<camera_id>/`
- **Type**: MJPEG stream (multipart/x-mixed-replace)
- **Auth**: Public (can be protected)
- **Example**: `http://localhost:8000/video_feed/2/`

### Camera Viewer Page
- **Endpoint**: `/camera/<camera_id>/`
- **Type**: HTML page with embedded stream
- **Auth**: Login required
- **Example**: `http://localhost:8000/camera/2/`

### Management Pages (All require login)
- **Cameras**: `http://localhost:8000/manage/cameras/`
- **AI Models**: `http://localhost:8000/manage/models/`
- **Face Identities**: `http://localhost:8000/manage/faces/`
- **Events**: `http://localhost:8000/manage/events/`
- **Alerts**: `http://localhost:8000/manage/alerts/`

---

## Key Files & How They Work

### Stream Generation
**File**: `feeds/video.py` → `generate_mjpeg(camera_id)`

```python
# Loads active models assigned to camera
active_models = camera.assigned_models.filter(is_active=True)

# For each frame:
# 1. Run inference on each active model
# 2. Draw detections on frame
# 3. Encode as JPEG
# 4. Yield as MJPEG chunk
```

### Model Management
**File**: `ai/models.py` → `AIModel` model

- **Fields**:
  - `name`: Model identifier
  - `model_type`: Type of detection (e.g., weapon, fire, person tracking)
  - `model_file`: Uploaded .pt/.onnx/.pb file
  - `is_active`: Boolean flag to enable/disable model
  - `confidence_threshold`: Minimum score for detections

### Camera Configuration
**File**: `feeds/models.py` → `CameraFeed` model

- **Fields**:
  - `protocol`: webcam, rtsp, http, file, etc.
  - `source`: Device index (0 for webcam), URL, or file path
  - `assigned_models`: M2M relationship to AIModels
  - `enabled`: Turn camera on/off

### Inference Engine
**File**: `ai/inference.py` → `ModelInferenceEngine`

- `load_model(path, type)`: Load .pt/.onnx/.pb files
- `run_inference(model, frame, type, threshold)`: Execute model on frame
- `FrameProcessor.draw_detections()`: Draw boxes and labels

---

## Troubleshooting

### Issue: Stream shows black/blank
- **Check 1**: Webcam accessible?
  ```powershell
  python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL'); cap.release()"
  ```
- **Check 2**: Camera source correct?
  - Go to `http://localhost:8000/manage/cameras/`
  - Verify "Webcam Feed" has source = "0"
- **Check 3**: Permissions
  - Django process needs webcam access
  - Some systems require special permissions

### Issue: Detection doesn't show
- **Check 1**: Model activated?
  - Go to Models page → look for green "ACTIVE" badge
  - If not, click "Activate" button
- **Check 2**: Model assigned to camera?
  - Edit "Webcam Feed" camera
  - Under "Assign AI Models", check your model box
  - Save camera
- **Check 3**: Model file exists?
  - Check `media/models/` directory
  - Look for your `.pt` file
- **Check 4**: Server logs
  - Look for errors like "Inference error" or "Cannot open source"

### Issue: Slow/laggy stream
- **Solution 1**: Lower webcam resolution in code
  - Edit `feeds/video.py` → adjust `generate_mjpeg`
- **Solution 2**: Reduce inference frequency
  - Only run inference every Nth frame
- **Solution 3**: Use faster model
  - Use a lightweight model or quantized version

---

## Next Steps

### Option 1: Use a Real Trained Model
- Train or download a YOLOv8 `.pt` model
- Upload via UI at `http://localhost:8000/manage/models/`
- Activate and assign to camera
- View live detection

### Option 2: Multiple Models
- Upload multiple models (weapon, fire, person)
- Activate all of them
- Assign all to webcam
- Stream will run all models simultaneously

### Option 3: Advanced Configuration
- Add more cameras (RTSP, HTTP streams, video files)
- Create custom alert rules
- Set up event detection
- Configure face recognition

---

## File Structure
```
media/
├── models/              ← Your .pt files upload here
│   └── your_model.pt
├── videos/              ← Video files for file-based cameras
├── face_identities/     ← Face images for recognition
└── alert_snapshots/     ← Captured alerts

feeds/
├── models.py            ← CameraFeed model
├── video.py             ← MJPEG stream generator (has inference loop)
├── views.py             ← Camera viewer template
└── management_views.py   ← Upload/edit endpoints

ai/
├── models.py            ← AIModel, FaceIdentity
└── inference.py         ← Model loading & inference
```

---

## Commands Reference

```powershell
# Start dev server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Clear model cache (if needed)
python manage.py shell
>>> from ai.inference import ModelInferenceEngine
>>> ModelInferenceEngine.clear_cache()

# Test webcam
python -c "import cv2; cap = cv2.VideoCapture(0); print(f'OK: {cap.get(3)}x{cap.get(4)}'); cap.release()"

# Setup (creates webcam camera)
python setup_webcam.py
```

---

## Support

For issues:
1. Check server logs (terminal where runserver is running)
2. Check browser console (F12 → Console tab)
3. Verify model file exists: `dir media/models/`
4. Verify webcam works: `python -c "import cv2; cv2.VideoCapture(0).isOpened()"`

---

**Last Updated**: February 3, 2026
**Version**: 1.0 - Initial webcam + detection setup
