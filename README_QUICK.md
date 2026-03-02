# 🎬 WEBCAM + .PT DETECTION - FINAL SUMMARY

## ✅ COMPLETE - What's Ready

✅ **Django Server** - Running at `http://localhost:8000`  
✅ **Webcam** - Camera 2 ("Webcam Feed") ready to stream  
✅ **MJPEG Stream** - Live video at `/video_feed/2/`  
✅ **AI Pipeline** - Inference integrated into stream  
✅ **Model Upload** - Accept .pt files at `/manage/models/`  
✅ **Browser UI** - All pages built and working  

---

## 🎯 WHAT YOU NEED TO DO

### ONE-TIME SETUP

#### 1. Create your user account
```powershell
cd C:\Workspace\RakshNetra
python manage.py createsuperuser
```
Then follow prompts (username, email, password)

---

### EVERY TIME YOU USE IT

#### 2. Open browser and login
```
http://localhost:8000/accounts/login/
```
→ Use credentials from step 1

#### 3. Upload your .pt model
Go to: `http://localhost:8000/manage/models/`
- Click **"+ Upload Model"**
- Fill in: Name, Type, File (.pt), Threshold
- Click **"Upload Model"**
- ✅ File saved to `media/models/`

#### 4. Activate model
On Models page:
- Find your model card
- Click **"Activate"** (turns green)

#### 5. Assign to webcam
Go to: `http://localhost:8000/manage/cameras/`
- Click **"Edit"** on "Webcam Feed"
- Check your model under "Assign AI Models"
- Click **"Save Camera"**

#### 6. View detection
- Click **"👁 View Live"** button
- OR go to: `http://localhost:8000/camera/2/`
- 📺 **See live webcam + detection boxes**

---

## 📂 WHERE YOUR FILES GO

| What | Where |
|------|-------|
| **Your .pt model** | `C:\Workspace\RakshNetra\media\models\your_file.pt` |
| **Video files** | `C:\Workspace\RakshNetra\media\videos\` |
| **Face images** | `C:\Workspace\RakshNetra\media\face_identities\` |

---

## 🔗 QUICK LINKS

| Page | URL |
|------|-----|
| Dashboard | `http://localhost:8000/` |
| Upload Model | `http://localhost:8000/manage/models/` |
| Manage Cameras | `http://localhost:8000/manage/cameras/` |
| Live Stream | `http://localhost:8000/camera/2/` |
| Raw MJPEG | `http://localhost:8000/video_feed/2/` |

---

## ⚡ COMMAND SHORTCUTS

```powershell
# Start server
python manage.py runserver

# CLI upload model (faster)
python quick_model.py upload "C:\path\model.pt" "Model Name" weapon_detection 0.5

# CLI activate
python quick_model.py activate 1

# CLI assign to webcam
python quick_model.py assign 1 2

# List all models
python quick_model.py list

# Test webcam
python -c "import cv2; print('OK' if cv2.VideoCapture(0).isOpened() else 'FAIL')"
```

---

## 🎨 WHAT YOU'LL SEE

### Models Page
```
✅ Your Model Name
   Type: Weapon Detection
   Status: 🟢 ACTIVE
   File: model.pt
   
   [Activate] [Edit] [Delete]
```

### Cameras Page
```
📹 Webcam Feed (ID: 2)
   Protocol: USB Webcam
   Source: 0
   Assigned Models: 1 ✓
   
   [👁 View Live] [Edit] [Enable/Disable] [Delete]
```

### Live Stream Page
```
┌─────────────────────────┐
│                         │
│  📹 LIVE WEBCAM        │
│                         │
│  [Box] Person (0.95)    │
│  [Box] Weapon (0.87)    │
│                         │
└─────────────────────────┘
```

---

## 🔧 REAL-TIME TROUBLESHOOTING

### Issue: Can't login
```
→ Check username/password (created via createsuperuser)
→ Go to http://localhost:8000/accounts/login/
```

### Issue: Model upload page is blank
```
→ Are you logged in? (check top right corner)
→ Go to http://localhost:8000/manage/models/
```

### Issue: No detection boxes on stream
```
✓ Is model ACTIVATED? (should be green)
✓ Is model ASSIGNED to camera? (edit camera, check box)
✓ Is model file in media/models/? (yes? check with file explorer)
✓ Try restarting server: Ctrl+C, then python manage.py runserver
```

### Issue: Blank/black video
```
✓ Is webcam working? (test: python quick_model.py list, then activate one)
✓ Is stream running? (logs show "Error streaming..."?)
✓ Try different camera source (edit camera, change Source to 1 instead of 0)
```

---

## 📋 CHECKLIST

- [ ] Created user account (superuser)
- [ ] Logged in at `http://localhost:8000`
- [ ] Uploaded .pt model to `/manage/models/`
- [ ] Activated model (green badge)
- [ ] Assigned model to camera (Edit → checkbox → Save)
- [ ] Clicked "👁 View Live" on camera
- [ ] See webcam stream
- [ ] See detection boxes/labels

---

## 🎓 TECHNICAL FLOW

```
Your .pt File
    ↓
Upload to http://localhost:8000/manage/models/
    ↓
Saved to: media/models/your_file.pt
    ↓
Click "Activate" button
    ↓
Model becomes is_active=True
    ↓
Go to Camera Management
    ↓
Edit "Webcam Feed" camera
    ↓
Check your model → Save
    ↓
Model assigned to camera.assigned_models
    ↓
Click "👁 View Live"
    ↓
Browser loads http://localhost:8000/camera/2/
    ↓
Django fetches CameraFeed (id=2)
    ↓
Requests /video_feed/2/ (MJPEG stream)
    ↓
generate_mjpeg(2) starts:
    • OpenCV captures from device 0
    • Loads all is_active=True assigned models
    • For each frame:
      - Runs inference on each model
      - Draws bounding boxes
      - Encodes as JPEG
      - Yields MJPEG chunk
    ↓
Browser receives stream
    ↓
📺 Live video + detection boxes visible
```

---

## 📞 HELP

**Server not running?**
```powershell
cd C:\Workspace\RakshNetra
python manage.py runserver
```

**Model won't upload?**
- File must be `.pt` format
- Check browser console (F12) for JS errors
- Check `media/models/` exists

**No detection showing?**
- Model must be ACTIVATED (green)
- Model must be ASSIGNED to camera
- Check server logs (look for "Inference error")

**Webcam not working?**
```powershell
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```
Should print `True`

---

## 🎉 YOU'RE READY!

Everything is set up. Just need to:
1. Create account
2. Login
3. Upload .pt file
4. Activate it
5. Assign to webcam
6. View stream

**That's it!** 🚀

---

**Server**: `http://localhost:8000`  
**Documentation**: See `COMPLETE_SETUP_GUIDE.md` for more details  
**Questions**: Check server logs or browser console (F12)

Good luck! 🎬📸
