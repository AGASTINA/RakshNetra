# 🚀 RakshNetra: Webcam Detection - READY TO USE

## ✅ What's Complete

1. **Webcam Support** - Device 0 (default webcam) is enabled and accessible
2. **Camera Created** - "Webcam Feed" (ID: 2) configured for `/video_feed/2/`
3. **Stream Working** - MJPEG stream generated at `/video_feed/2/` endpoint
4. **AI Integration** - Inference pipeline wired into stream generator
5. **Model Upload** - `.pt` files upload to `media/models/` via web UI
6. **Detection Ready** - Models automatically run on every frame when assigned to camera

---

## 📍 WHERE TO UPLOAD YOUR .pt FILE

### Via Web UI (Recommended)
1. Start server: `python manage.py runserver`
2. Login: `http://localhost:8000/accounts/login/`
3. Upload model: `http://localhost:8000/manage/models/`
   - Click **"+ Upload Model"**
   - Select model type (e.g., "Weapon Detection")
   - Upload your `.pt` file
   - Set confidence threshold
   - Click **"Upload Model"**
4. File saves to: **`C:\Workspace\RakshNetra\media\models\your_file.pt`**

### Via Command Line (Quick)
```powershell
python quick_model.py upload "C:\path\to\your_model.pt" "My Detection Model" weapon_detection 0.5
python quick_model.py activate <model_id>
python quick_model.py assign <model_id> 2
```

---

## 🎬 ENABLE WEBCAM DETECTION (5 Steps)

### 1. Start Server
```powershell
cd C:\Workspace\RakshNetra
python manage.py runserver
```
→ Server runs at `http://localhost:8000`

### 2. Login
- Go to `http://localhost:8000/accounts/login/`
- Enter your credentials

### 3. Upload & Activate Model
- Go to `http://localhost:8000/manage/models/`
- Upload your `.pt` file
- Click **"Activate"** button (turns green when active)

### 4. Assign to Webcam
- Go to `http://localhost:8000/manage/cameras/`
- Click **"Edit"** on "Webcam Feed" camera
- Check your model under "Assign AI Models"
- Click **"Save Camera"**

### 5. View Detection Stream
- Click **"👁 View Live"** on camera card
- OR go to: `http://localhost:8000/camera/2/`
- **You'll see your webcam with detection boxes overlaid**

---

## 📊 How Detection Works

```
Webcam Frame (30fps)
    ↓
  OpenCV captures raw frame
    ↓
  Load Active Models (e.g., weapon detection)
    ↓
  Run Inference on Frame
    ↓
  Draw Bounding Boxes + Labels
    ↓
  Encode as JPEG
    ↓
  Stream as MJPEG to Browser
```

---

## 🎯 Key Endpoints

| What | URL | Notes |
|------|-----|-------|
| **Dashboard** | `http://localhost:8000/` | Shows overview |
| **Upload Model** | `http://localhost:8000/manage/models/` | .pt files go here |
| **Manage Cameras** | `http://localhost:8000/manage/cameras/` | Assign models to cameras |
| **Live Stream (Raw)** | `http://localhost:8000/video_feed/2/` | MJPEG stream (unauthenticated) |
| **Live Viewer (UI)** | `http://localhost:8000/camera/2/` | Viewer page (requires login) |

---

## 📁 File Locations

| Type | Directory | Upload Via |
|------|-----------|-----------|
| **AI Models** | `media/models/` | Web UI at `/manage/models/` |
| **Video Files** | `media/videos/` | Camera form (Protocol: "Video File") |
| **Face Images** | `media/face_identities/` | Web UI at `/manage/faces/` |

---

## 🛠️ Troubleshooting

### Webcam not working?
```powershell
# Test if webcam is accessible
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Detection not showing?
- ✓ Model is **Activated** (green badge)?
- ✓ Model is **Assigned** to camera?
- ✓ Model file exists in `media/models/`?
- ✓ Check server logs for errors

### Model upload failed?
- ✓ File is `.pt` format?
- ✓ You have write permissions to `media/models/`?
- ✓ File isn't corrupted?

---

## 📝 Quick Commands

```powershell
# Setup webcam camera
python setup_webcam.py

# Upload model from CLI
python quick_model.py upload "path/to/model.pt" "Model Name" weapon_detection

# Activate model
python quick_model.py activate 1

# Assign to webcam
python quick_model.py assign 1 2

# List all models
python quick_model.py list

# Start server
python manage.py runserver

# Create superuser (first time)
python manage.py createsuperuser
```

---

## 🎓 Architecture

**Stream Generation** (`feeds/video.py`):
```python
# For each frame:
1. Capture from webcam via OpenCV
2. Get active models assigned to camera
3. Run inference on each model
4. Draw detection boxes
5. Encode as JPEG
6. Yield as MJPEG chunk
```

**Model Management** (`ai/models.py`):
- Upload `.pt` / `.onnx` / `.pb` files
- Set confidence threshold
- Activate/deactivate models
- Assign to multiple cameras

**Camera Config** (`feeds/models.py`):
- Support multiple protocols (webcam, RTSP, HTTP, file)
- Assign multiple models per camera
- Enable/disable streams

---

## ✨ Features Ready to Use

- ✅ **Webcam Streaming**: Live 30fps MJPEG from device 0
- ✅ **Model Upload**: `.pt` files save to `media/models/`
- ✅ **AI Inference**: Active models run on every frame
- ✅ **Detection Visualization**: Bounding boxes + labels overlay
- ✅ **Multi-Model**: Run multiple models simultaneously
- ✅ **Web UI**: Upload, manage, activate models via browser
- ✅ **REST API**: Endpoints for programmatic access

---

## 🔜 Next Steps

1. **Get a trained model**: Use YOLOv8, YOLOv5, or your custom `.pt` model
2. **Upload via UI**: `http://localhost:8000/manage/models/`
3. **Activate model**: Click "Activate" button
4. **Assign to camera**: Edit "Webcam Feed" → check model → save
5. **View detection**: Click "👁 View Live" or go to `/camera/2/`

---

## 📞 Support

- **Logs**: Check terminal where `runserver` is running
- **Browser console**: F12 → Console tab for JS errors
- **Files**: Check `media/` directory for uploads
- **Webcam**: Test with `python -c "import cv2; cv2.VideoCapture(0)..."`

---

**Server Status**: ✅ Running on `http://localhost:8000`
**Webcam Camera**: ✅ Created (ID: 2, Device 0)
**Stream Endpoint**: ✅ Active at `/video_feed/2/`

🎬 **You're ready to stream and detect!**
