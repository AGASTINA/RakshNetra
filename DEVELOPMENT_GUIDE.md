# RakshNetra Development Guide

## What's Been Implemented ✅

### 1. **User Authentication System**
- ✅ User signup with role assignment (Viewer, Operator, Commander)
- ✅ Login/logout functionality
- ✅ Password validation (minimum 12 characters)
- ✅ User profile management
- **Files:**
  - `accounts/views.py` - Auth views
  - `templates/accounts/login.html` - Login page
  - `templates/accounts/signup.html` - Signup page

### 2. **Camera Management**
- ✅ Support for multiple protocols:
  - USB Webcam (device index)
  - RTSP (IP cameras/CCTV)
  - RTMP streaming
  - HTTP/HTTPS streams
  - HLS (m3u8 streams)
  - Local video files
- ✅ Two stream modes: Preview (Browser) & AI Mode (OpenCV)
- ✅ Enable/disable cameras
- ✅ Assign AI models to cameras
- **Files:**
  - `feeds/models.py` - CameraFeed model
  - `feeds/management_views.py` - Camera CRUD views
  - `templates/management/cameras.html` - Camera UI
  - REST API: `/api/cameras/` endpoints

### 3. **AI Model Management**
- ✅ Model upload (supports .pt PyTorch, .onnx, .pb)
- ✅ Model types: Weapon Detection, Fire/Smoke, Behavior, Vehicle, Face Recognition, etc.
- ✅ Confidence threshold configuration
- ✅ Model activation/deactivation
- ✅ Inference engine with preprocessing
- **Files:**
  - `ai/models.py` - AIModel, FaceIdentity models
  - `ai/inference.py` - Model loading & inference engine
  - `ai/api.py` - AI REST APIs
  - `templates/management/models.html` - Model UI
  - REST API: `/api/ai/models/`, `/api/ai/faces/`

### 4. **REST APIs**
Full CRUD APIs with filtering and actions:

**Camera APIs:**
```
GET/POST   /api/cameras/              - List/create cameras
GET/PUT    /api/cameras/{id}/         - Read/update camera
DELETE     /api/cameras/{id}/         - Delete camera
POST       /api/cameras/{id}/toggle_enabled/  - Enable/disable
POST       /api/cameras/{id}/assign_models/   - Assign models
GET        /api/cameras/protocols/    - List protocols
GET        /api/cameras/modes/        - List modes
```

**AI Model APIs:**
```
GET/POST   /api/ai/models/            - List/upload models
GET/PUT    /api/ai/models/{id}/       - Read/update model
DELETE     /api/ai/models/{id}/       - Delete model
POST       /api/ai/models/{id}/toggle_active/      - Activate/deactivate
POST       /api/ai/models/{id}/update_threshold/   - Set confidence
POST       /api/ai/models/{id}/add_activation_rule/ - Add trigger
GET        /api/ai/models/types/      - List model types
GET        /api/ai/models/active/     - Get active models
```

**Alert APIs:**
```
GET/POST   /api/alerts/               - List/create alerts
GET        /api/alerts/critical/      - Critical alerts only
GET        /api/alerts/recent/        - Last 24 hours
GET        /api/alerts/severities/    - List severity levels
```

### 5. **Management UI**
Four comprehensive management pages:

1. **Camera Management** (`/manage/cameras/`)
   - Add/edit/delete cameras
   - Configure protocol and source
   - Assign AI models
   - Toggle camera status

2. **Model Management** (`/manage/models/`)
   - Upload new models
   - Set confidence thresholds
   - Activate/deactivate models
   - Delete models

3. **Alert Management** (`/manage/alerts/`)
   - View all alerts with timestamps
   - Filter by severity (Critical/Warning/Info)
   - Filter by camera
   - View snapshots

4. **Events Management** (`/manage/events/`)
   - View operations events
   - Display threat levels
   - Event location and timeline

### 6. **Dashboard**
- Login-protected dashboard
- Navigation menu linking all management pages
- Video grid layout (ready for camera feeds)
- Real-time alert feed area

## How to Use

### 1. **First Time Setup**

```powershell
# The app should already be running, but if you need to start it:
cd c:\Workspace\RakshNetra
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Visit: **http://localhost:8000/**

### 2. **Create Your First Account**

1. Click "Sign up" on the login page
2. Fill in:
   - Username: your choice
   - Email: your@email.com
   - Password: min 12 characters
   - Role: Choose Operator or Viewer
3. Login with your credentials

### 3. **Add Your First Camera**

1. Go to **Cameras** (top menu)
2. Click **+ Add Camera**
3. Fill in:
   - **Camera Name**: e.g., "Main Entrance"
   - **Protocol**: Select USB Webcam, RTSP, or file
   - **Source**: 
     - USB Webcam: `0` (default) or device index
     - RTSP: `rtsp://192.168.1.100:554/stream`
     - HTTP: `http://camera.local/stream`
     - File: `/path/to/video.mp4`
   - **Mode**: Preview or AI Mode
4. Optionally assign AI models
5. Click **Save Camera**

### 4. **Upload an AI Model**

1. Go to **AI Models**
2. Click **+ Upload Model**
3. Fill in:
   - **Model Name**: e.g., "YOLOv8 Weapon Detection"
   - **Model Type**: Choose detection type
   - **Model File**: Upload `.pt` or `.onnx` file
   - **Confidence Threshold**: 0.5 (default)
   - **Description**: Optional
4. Click **Upload Model**
5. The model appears in your models list

### 5. **View Alerts & Events**

1. Go to **Alerts** to see detected threats
   - Filter by severity or camera
   - View snapshots if available
2. Go to **Events** to see operations timeline

### 6. **API Usage Examples**

Get all cameras:
```bash
curl http://localhost:8000/api/cameras/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Create a new camera:
```bash
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Side Gate",
    "protocol": "rtsp",
    "source": "rtsp://camera.local/stream",
    "mode": "ai",
    "enabled": true
  }'
```

List active AI models:
```bash
curl http://localhost:8000/api/ai/models/active/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Next Steps to Complete

### Important Remaining Work:

1. **WebSocket Integration** (Real-time alerts)
   - Connect alert system to real-time streaming
   - Live video feed updates via channels

2. **Full Model Inference**
   - Load actual trained models (.pt files)
   - Run frame-by-frame inference
   - Draw bounding boxes on video

3. **Advanced Features**
   - Situational map with camera locations
   - Multi-camera tracking
   - Report generation (PDF exports)
   - Face recognition database
   - Event-triggered recording

4. **Security Hardening**
   - Token-based authentication (JWT)
   - Role-based access control (RBAC)
   - API rate limiting
   - Input validation & sanitization

5. **Deployment**
   - Redis configuration for production
   - Gunicorn/uWSGI WSGI server
   - Nginx reverse proxy setup
   - SSL/TLS certificates
   - Docker containerization

## Project Structure

```
RakshNetra/
├── accounts/          # User authentication
├── feeds/             # Camera feeds & alerts
├── ai/                # AI models & inference
├── events/            # Event management
├── situational_map/   # Map & tracking
├── reports/           # Report generation
├── rakshnetra/        # Main settings & routing
├── templates/         # HTML templates
│   ├── accounts/      # Auth pages
│   └── management/    # Management UIs
├── static/            # CSS, JS, images
└── media/             # Uploaded models, images

```

## Database Models

### Key Tables:
- **User** - Extended Django user with roles
- **CameraFeed** - Configured camera sources
- **AIModel** - Uploaded AI models with metadata
- **Alert** - Detected threats & anomalies
- **Event** - Operations events
- **FaceIdentity** - Face recognition database

## API Documentation

Full REST API endpoints available at `/api/` with DRF browsable interface when DEBUG=True.

All endpoints require authentication (except `/accounts/`).

## Testing the System

1. **Test API endpoints** using the REST interface at `/api/`
2. **Test camera management** by adding multiple cameras
3. **Test model upload** with sample .pt or .onnx files
4. **Monitor alerts** in real-time via the UI

## Performance Notes

- **In-Memory Channels**: Using in-memory channel layer (dev only)
- **SQLite Database**: Development database (use PostgreSQL in production)
- **Model Caching**: Models cached after first load
- **Frame Buffering**: Latest frame buffered for efficiency

## Troubleshooting

**Issue**: "Camera not found" when accessing video feed
- **Solution**: Check camera source is correct (protocol://source)

**Issue**: Models not loading
- **Solution**: Ensure PyTorch/ONNX packages installed; check file format

**Issue**: WebSocket connection errors
- **Solution**: For production, set up Redis: `CHANNEL_LAYERS` in settings

---

**Last Updated**: February 1, 2026
**Status**: MVP Ready - Ready for Feature Development
