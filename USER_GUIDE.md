# RakshNetra - User Guide

## Quick Start

### 1. **Adding a Webcam**

Go to **Cameras** → **+ Add Camera**

Fill in:
- **Camera Name**: Any name (e.g., "Front Entrance")
- **Protocol**: Select "USB Webcam"
- **Source**: Enter `0` for the default webcam (or `1`, `2`, etc. for multiple webcams)
- **Stream Mode**: "Preview Mode (Browser)"
- Click **Add Camera**

Then go to **Cameras**, find your camera, and click **👁 View Live** to see the webcam stream.

---

### 2. **Uploading Your Trained AI Model (.pt file)**

Go to **AI Models** → **+ Upload Model**

Fill in:
- **Model Name**: Your model name (e.g., "YOLOv8 Weapon Detection")
- **Model Type**: "PyTorch" (for .pt files)
- **Model File**: Select your `.pt` file
- **Confidence Threshold**: 0.5 (or your preferred value, 0.0-1.0)
- **Description**: (optional)
- Click **Upload Model**

Your model file is saved to: `media/models/`

The model will appear in the AI Models grid. You can then:
- Click **Activate** to enable it
- Assign it to cameras by editing a camera and checking the model

---

### 3. **Uploading Video Files for Analysis**

Currently, you can add video files as camera sources:

Go to **Cameras** → **+ Add Camera**

- **Camera Name**: Any name
- **Protocol**: Select "Video File"
- **Source**: Full path to your video file (e.g., `C:/Videos/security_footage.mp4`)
- **Stream Mode**: "Preview Mode (Browser)"
- Click **Add Camera**

Then view it like a webcam by clicking **👁 View Live**

---

### 4. **What Each Page Does**

| Page | Purpose |
|------|---------|
| **Dashboard** | Overview of all cameras and alerts |
| **Cameras** | Add, edit, delete, and view camera feeds |
| **AI Models** | Upload, activate, and manage AI models |
| **Alerts** | View detected threats and alerts |
| **Events** | Create and manage security events |

---

### 5. **Camera Protocols Explained**

- **USB Webcam**: Local webcam (source: `0` or device index)
- **RTSP**: IP cameras (source: `rtsp://ip:port/stream`)
- **RTMP**: Streaming servers (source: `rtmp://server/stream`)
- **HTTP/HTTPS**: Streaming URLs (source: `http://...`)
- **HLS**: Live streams (source: `http://...stream.m3u8`)
- **Video File**: Local video files (source: `/path/to/video.mp4`)

---

### 6. **AI Model Setup**

Your models should be:
- **Format**: `.pt` (PyTorch), `.onnx`, or `.pb` (TensorFlow)
- **Location**: Upload via UI → auto-saved to `media/models/`
- **Activation**: Activate in the Models grid after uploading
- **Assignment**: Edit a camera and select models to apply

---

### 7. **File Locations**

```
c:\Workspace\RakshNetra\
├── media/
│   ├── models/                    ← Your .pt files go here
│   ├── alert_snapshots/           ← Alert images
│   └── face_identities/           ← Faces for recognition
├── templates/                      ← UI pages
├── static/                         ← CSS/JS
└── manage.py                       ← Django control script
```

---

### 8. **Common Issues & Solutions**

**Q: Camera shows "ACTIVE" but doesn't stream**
- Ensure your webcam is connected and not used by another app
- Try different device indices (0, 1, 2...)
- For IP cameras, verify RTSP URL is correct

**Q: Model upload successful but not appearing**
- Refresh the page
- Check browser console (F12) for errors
- Ensure file is .pt, .onnx, or .pb format

**Q: "Can't reach the page" error**
- Make sure Django server is running:
  ```
  python manage.py runserver 127.0.0.1:8000
  ```
- Server should be at `http://127.0.0.1:8000/`

**Q: Models don't run inference on video**
- This requires PyTorch/ONNX installed: `pip install torch onnxruntime`
- Models must be activated in the Models grid first
- Models must be assigned to a camera

---

### 9. **File Upload Locations**

| File Type | Upload Location | Path |
|-----------|-----------------|------|
| AI Models (.pt) | AI Models page | `media/models/` |
| Alert Snapshots | Auto-generated | `media/alert_snapshots/` |
| Face Database | Face ID upload | `media/face_identities/` |

---

### 10. **Next Steps**

1. ✅ Add a webcam camera
2. ✅ Upload your .pt model
3. ✅ Assign model to camera
4. ✅ View live stream with AI analysis

