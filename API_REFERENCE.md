# RakshNetra API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
All `/api/` endpoints require login. Use session cookies (automatically handled in browser).

For programmatic access, you'll need token authentication (to be implemented).

---

## Authentication Endpoints

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/signup/` | Create new user account |
| POST | `/accounts/login/` | User login |
| GET | `/accounts/logout/` | User logout |
| GET | `/accounts/profile/` | View user profile |

---

## Camera Feed Endpoints

### List & Create Cameras
```
GET  /api/cameras/              # List all cameras
POST /api/cameras/              # Create new camera
```

**Example POST:**
```json
{
  "name": "Main Gate",
  "protocol": "rtsp",
  "source": "rtsp://192.168.1.100:554/stream",
  "mode": "ai",
  "enabled": true
}
```

### Retrieve, Update, Delete
```
GET    /api/cameras/{id}/       # Get camera details
PUT    /api/cameras/{id}/       # Update camera
DELETE /api/cameras/{id}/       # Delete camera
```

### Camera Actions
```
POST   /api/cameras/protocols/       # List available protocols
POST   /api/cameras/modes/           # List available modes
POST   /api/cameras/{id}/toggle_enabled/  # Enable/disable camera
POST   /api/cameras/{id}/assign_models/   # Assign AI models to camera
```

**Assign Models:**
```json
POST /api/cameras/{id}/assign_models/
{
  "model_ids": [1, 2, 3]
}
```

---

## AI Model Endpoints

### List & Create Models
```
GET  /api/ai/models/            # List all models
POST /api/ai/models/            # Upload new model
```

**Example POST (multipart/form-data):**
```
name: "YOLOv8 Weapon Detection"
model_type: "weapon_detection"
model_file: (binary file)
confidence_threshold: 0.5
description: "Detects weapons in video feeds"
```

### Retrieve, Update, Delete
```
GET    /api/ai/models/{id}/     # Get model details
PUT    /api/ai/models/{id}/     # Update model
DELETE /api/ai/models/{id}/     # Delete model
```

### Model Actions
```
GET  /api/ai/models/types/              # List model types
GET  /api/ai/models/active/             # Get active models only
POST /api/ai/models/{id}/toggle_active/ # Activate/deactivate
POST /api/ai/models/{id}/update_threshold/ # Update confidence threshold
POST /api/ai/models/{id}/add_activation_rule/ # Add trigger rule
```

**Available Model Types:**
- `weapon_detection` - Weapon Detection
- `fire_smoke` - Fire/Smoke Detection
- `suspicious_behavior` - Suspicious Behavior
- `vehicle_detection` - Vehicle Detection
- `person_tracking` - Person Tracking
- `face_recognition` - Face Recognition
- `nsg_classification` - NSG vs Non-NSG Classification

**Update Threshold:**
```json
POST /api/ai/models/{id}/update_threshold/
{
  "confidence_threshold": 0.7
}
```

**Add Activation Rule:**
```json
POST /api/ai/models/{id}/add_activation_rule/
{
  "trigger": "motion_detected",
  "enabled": true
}
```

---

## Alert Endpoints

### List & Create Alerts
```
GET  /api/alerts/               # List all alerts
POST /api/alerts/               # Create new alert (system use)
```

### Retrieve, Update, Delete
```
GET    /api/alerts/{id}/        # Get alert details
PUT    /api/alerts/{id}/        # Update alert
DELETE /api/alerts/{id}/        # Delete alert
```

### Alert Filters
```
GET  /api/alerts/severities/    # List severity levels
GET  /api/alerts/critical/      # Critical alerts only
GET  /api/alerts/recent/        # Alerts from last 24 hours
```

**Alert Severity Levels:**
- `info` - Information
- `warning` - Warning
- `critical` - Critical

**Alert Response:**
```json
{
  "id": 1,
  "event": 1,
  "camera": 1,
  "camera_name": "Main Gate",
  "threat_type": "Weapon Detected",
  "severity": "critical",
  "confidence": 0.95,
  "timestamp": "2026-02-01T12:34:56Z",
  "snapshot": "media/alert_snapshots/snapshot_1.jpg",
  "location": "Building A, Ground Floor",
  "metadata": {}
}
```

---

## Event Endpoints

### List & Create Events
```
GET  /api/events/               # List all events
POST /api/events/               # Create new event
```

**Example POST:**
```json
{
  "name": "Building A Perimeter",
  "start_time": "2026-02-01T08:00:00Z",
  "end_time": "2026-02-01T18:00:00Z",
  "location": "Building A, North Side",
  "coordinates": "40.7128,-74.0060",
  "threat_level": "high",
  "description": "Security event for building perimeter",
  "vip_notes": "VIP visit in progress"
}
```

### Retrieve, Update, Delete
```
GET    /api/events/{id}/        # Get event details
PUT    /api/events/{id}/        # Update event
DELETE /api/events/{id}/        # Delete event
```

**Threat Levels:**
- `low` - Low
- `medium` - Medium
- `high` - High

---

## Face Identity Endpoints

### List & Create Face Records
```
GET  /api/ai/faces/             # List all face records
POST /api/ai/faces/             # Create new face record
```

### Retrieve, Update, Delete
```
GET    /api/ai/faces/{id}/      # Get face record
PUT    /api/ai/faces/{id}/      # Update face record
DELETE /api/ai/faces/{id}/      # Delete face record
```

### Face Filters
```
GET  /api/ai/faces/types/       # List face identity types
GET  /api/ai/faces/by_type/?type=nsg  # Filter by type
```

**Face Identity Types:**
- `nsg` - NSG Personnel
- `suspect` - Known Suspect
- `unknown` - Unknown

---

## Protocol Reference

### USB Webcam
```
Protocol: webcam
Source: 0 (device index)
Example: "0" for /dev/video0
```

### RTSP (IP Cameras)
```
Protocol: rtsp
Source: rtsp://hostname:554/path
Example: "rtsp://192.168.1.100:554/stream"
```

### RTMP Streaming
```
Protocol: rtmp
Source: rtmp://hostname/app/stream
Example: "rtmp://streaming.server/live/stream1"
```

### HTTP/HTTPS
```
Protocol: http
Source: http://hostname/stream/path
Example: "http://camera.local:8080/video.mjpeg"
```

### HLS (m3u8)
```
Protocol: hls
Source: http://hostname/path/stream.m3u8
Example: "http://streaming.server/live/stream.m3u8"
```

### Local Video File
```
Protocol: file
Source: /absolute/path/to/file.mp4
Example: "C:/Videos/camera_feed.mp4"
```

---

## Response Format

All responses follow REST conventions:

### Success (200, 201)
```json
{
  "id": 1,
  "name": "Main Gate",
  "protocol": "rtsp",
  ...
}
```

### List Responses (DRF Pagination)
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/cameras/?page=2",
  "previous": null,
  "results": [
    { "id": 1, ... },
    { "id": 2, ... }
  ]
}
```

### Error (400, 404, 500)
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Filtering & Pagination

### Query Parameters
```
?page=2                 # Pagination
?search=Main           # Search by name/text
?ordering=-timestamp   # Sort (- for descending)
```

### Camera Filtering
```
GET /api/cameras/?enabled=true
GET /api/cameras/?protocol=rtsp
GET /api/cameras/?mode=ai
```

### Alert Filtering
```
GET /api/alerts/?severity=critical
GET /api/alerts/?camera=1
GET /api/alerts/?ordering=-timestamp
```

---

## Example cURL Requests

### Get All Cameras
```bash
curl http://localhost:8000/api/cameras/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

### Create a Camera
```bash
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "name": "Front Door",
    "protocol": "rtsp",
    "source": "rtsp://192.168.1.100:554/stream",
    "mode": "ai",
    "enabled": true
  }'
```

### Get Active Models
```bash
curl http://localhost:8000/api/ai/models/active/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

### Get Critical Alerts
```bash
curl http://localhost:8000/api/alerts/critical/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Deletion successful |
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - Not authenticated |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Internal error |

---

## Frontend Pages

| URL | Description |
|-----|-------------|
| `/` | Main dashboard (login required) |
| `/accounts/signup/` | User registration |
| `/accounts/login/` | User login |
| `/accounts/logout/` | User logout |
| `/accounts/profile/` | User profile |
| `/manage/cameras/` | Camera management UI |
| `/manage/models/` | Model management UI |
| `/manage/alerts/` | Alert viewer UI |
| `/manage/events/` | Event management UI |
| `/api/` | API root (DRF browsable interface) |
| `/admin/` | Django admin panel |

---

*API Reference - RakshNetra v1.0*
*Last Updated: February 1, 2026*
