# RakshNetra - Setup Instructions

## ✅ System Status

- **Server**: Running on `http://127.0.0.1:8000/`
- **Database**: SQLite (local)
- **Authentication**: Required (login/signup)
- **All Migrations**: Applied ✓

---

## 🎥 **Camera Setup**

### Adding a Webcam (USB Camera)

1. Go to **Cameras** management page
2. Click **+ Add Camera**
3. Fill in:
   - **Name**: Your camera name
   - **Protocol**: `USB Webcam`
   - **Source**: `0` (or `1`, `2` for multiple webcams)
   - **Mode**: `Preview Mode (Browser)`
4. Click **Add Camera**
5. Click **👁 View Live** to see the stream

### Adding an IP Camera (RTSP)

1. Go to **Cameras**
2. Click **+ Add Camera**
3. Fill in:
   - **Name**: Camera name
   - **Protocol**: `RTSP (IP Camera/CCTV)`
   - **Source**: `rtsp://192.168.1.100:554/stream` (your camera URL)
   - **Mode**: `Preview Mode (Browser)`
4. Click **Add Camera**
5. View with **👁 View Live**

### Adding Video Files

1. Go to **Cameras**
2. Click **+ Add Camera**
3. Fill in:
   - **Name**: Video name
   - **Protocol**: `Video File`
   - **Source**: Full path like `C:/Videos/footage.mp4`
   - **Mode**: `Preview Mode (Browser)`
4. Click **Add Camera**
5. View with **👁 View Live**

---

## 🤖 **AI Model Upload**

### Where to Upload Your .pt Model

1. Go to **AI Models** page
2. Click **+ Upload Model**
3. Fill in:
   - **Model Name**: Your model name (e.g., "YOLOv8 Weapon Detection")
   - **Model Type**: `PyTorch` (for .pt files)
   - **Model File**: Select your `.pt` file
   - **Confidence Threshold**: `0.5` (or preferred value)
   - **Description**: Optional description
4. Click **Upload Model**

### Where Files Are Stored

Your uploaded models are automatically saved to:
```
c:\Workspace\RakshNetra\media\models\
```

You can see them listed in the **AI Models** grid after upload.

### Using Models with Cameras

1. Upload your model (see above)
2. Click **Activate** on the model card
3. Go to **Cameras**
4. Edit a camera
5. In "Assign AI Models", check your model
6. Save changes
7. View **👁 Live** to see AI inference on the video

---

## 📹 **Video Upload**

There are two ways to use video files:

### Method 1: Add as Camera Source
1. Go to **Cameras** → **+ Add Camera**
2. Protocol: `Video File`
3. Source: Full path to `.mp4` or `.avi` file
4. Click **👁 View Live**

### Method 2: Upload Model & View
1. Upload your AI model
2. Add video file as camera
3. Assign model to camera
4. Watch AI inference on video

---

## 📊 **File Storage Locations**

| Type | Location | Access |
|------|----------|--------|
| **AI Models (.pt)** | `media/models/` | Upload via UI |
| **Alert Images** | `media/alert_snapshots/` | Auto-generated |
| **Face Database** | `media/face_identities/` | Future feature |
| **Static Assets** | `static/` | CSS/JS files |
| **Templates** | `templates/` | HTML pages |

---

## 🚀 **Quick Reference**

### Server Commands

```powershell
# Start server
cd c:\Workspace\RakshNetra
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

# Run migrations
.\.venv\Scripts\python.exe manage.py migrate

# Create superuser
.\.venv\Scripts\python.exe manage.py createsuperuser
```

### URLs

| Page | URL |
|------|-----|
| Dashboard | `http://127.0.0.1:8000/` |
| Cameras | `http://127.0.0.1:8000/manage/cameras/` |
| AI Models | `http://127.0.0.1:8000/manage/models/` |
| Alerts | `http://127.0.0.1:8000/manage/alerts/` |
| Events | `http://127.0.0.1:8000/manage/events/` |
| Camera Live | `http://127.0.0.1:8000/camera/<id>/` |

---

## ❓ **Troubleshooting**

### "Can't reach the page" or 127.0.0.1 refused connection
- Check if server is running: `python manage.py runserver 127.0.0.1:8000`
- Server should show: `Starting development server at http://127.0.0.1:8000/`

### Webcam not streaming
- Ensure webcam is connected and not in use by another app
- Try source `0`, `1`, `2` (device index)
- Check browser console (F12) for errors

### Model upload shows success but doesn't appear
- Refresh the page
- Check `media/models/` directory for files
- Ensure file is .pt, .onnx, or .pb

### "No such table" errors
- Run migrations: `python manage.py migrate`
- This creates all database tables

---

## 📝 **Workflow Example**

1. **Start Server**
   ```
   python manage.py runserver 127.0.0.1:8000
   ```

2. **Login/Signup**
   - Visit http://127.0.0.1:8000/
   - Create account or login

3. **Add Webcam**
   - Go to Cameras
   - Add camera with source `0`
   - Click View Live to see stream

4. **Upload Model**
   - Go to AI Models
   - Upload your trained `.pt` file
   - Click Activate

5. **Connect Model to Camera**
   - Edit camera
   - Assign your model
   - View Live to see AI inference

---

## 🎯 **Next Steps**

✅ Server is running
✅ Database is set up
✅ Authentication works
✅ Camera streaming ready
✅ Model upload ready

**What to do now:**
1. Add your webcam (source: 0)
2. Upload your trained .pt model
3. Assign model to camera
4. View live stream with AI inference

