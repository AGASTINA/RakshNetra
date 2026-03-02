#!/usr/bin/env python
"""
Comprehensive Video Detection Script
Processes a video with ALL available detection models:
- Object Detection (YOLO)
- Face Recognition
- Weapon Detection
- Suspicious Activities Detection

Usage: python detect_video_all.py <video_path>
"""

import os
import sys
import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
import django
django.setup()

from ai.inference import ModelInferenceEngine

# Model paths
MODELS = {
    'object_detection': 'media/models/best (5).pt',
    'weapon_detection': 'media/models/weapon_detection_model.pt',
    'suspicious_activities': 'media/models/Suspicious_Activities_nano.pt',
}

# Colors for drawing
COLORS = {
    'person': (0, 255, 0),      # Green
    'weapon': (0, 0, 255),       # Red
    'suspicious': (0, 165, 255), # Orange
    'face': (255, 0, 0),         # Blue
    'person_activity': (255, 255, 0),  # Cyan
}


def load_all_models():
    """Load all available detection models"""
    print("\n📦 Loading Detection Models...")
    models = {}
    for model_name, model_path in MODELS.items():
        if not os.path.exists(model_path):
            print(f"  ⚠️  {model_name} not found at {model_path}")
            continue
        print(f"  📥 Loading {model_name}...")
        try:
            model = ModelInferenceEngine.load_model(model_path, model_name)
            if model:
                models[model_name] = model
                print(f"  ✅ {model_name} loaded successfully")
            else:
                print(f"  ❌ Failed to load {model_name}")
        except Exception as e:
            print(f"  ❌ Error loading {model_name}: {e}")
    
    print(f"\n✅ Loaded {len(models)} detection models\n")
    return models


def run_all_detections(frame, models, confidence_threshold=0.5):
    """Run all detection models on a frame"""
    detections = {
        'all_objects': [],
        'weapons': [],
        'suspicious': [],
        'persons': [],
    }
    
    # Object Detection
    if 'object_detection' in models:
        try:
            result = ModelInferenceEngine.run_inference(
                models['object_detection'],
                frame,
                'object_detection',
                confidence_threshold
            )
            if 'detections' in result:
                detections['all_objects'] = result['detections']
                # Filter persons
                detections['persons'] = [d for d in result['detections'] if 'person' in d.get('label', '').lower()]
        except Exception as e:
            print(f"Error in object detection: {e}")
    
    # Weapon Detection
    if 'weapon_detection' in models:
        try:
            result = ModelInferenceEngine.run_inference(
                models['weapon_detection'],
                frame,
                'weapon_detection',
                confidence_threshold
            )
            if 'detections' in result:
                detections['weapons'] = result['detections']
        except Exception as e:
            print(f"Error in weapon detection: {e}")
    
    # Suspicious Activities Detection
    if 'suspicious_activities' in models:
        try:
            result = ModelInferenceEngine.run_inference(
                models['suspicious_activities'],
                frame,
                'suspicious_activities',
                confidence_threshold * 0.8  # Lower threshold for activities
            )
            if 'detections' in result:
                detections['suspicious'] = result['detections']
        except Exception as e:
            print(f"Error in suspicious activities detection: {e}")
    
    return detections


def draw_detections(frame, detections):
    """Draw all detections on frame with color coding"""
    frame_with_boxes = frame.copy()
    
    # Draw objects (green)
    for det in detections['all_objects']:
        if 'bbox' in det:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            label = f"{det.get('label', 'Object')} {det.get('confidence', 0):.2f}"
            color = COLORS.get(det.get('label', '').lower(), (0, 255, 0))
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame_with_boxes, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Draw weapons (red)
    for det in detections['weapons']:
        if 'bbox' in det:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            label = f"⚠️ WEAPON {det.get('confidence', 0):.2f}"
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), COLORS['weapon'], 3)
            cv2.putText(frame_with_boxes, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['weapon'], 2)
    
    # Draw suspicious activities (orange)
    for det in detections['suspicious']:
        if 'bbox' in det:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            label = f"⚠️ SUSPICIOUS {det.get('confidence', 0):.2f}"
            cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), COLORS['suspicious'], 2)
            cv2.putText(frame_with_boxes, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS['suspicious'], 2)
    
    return frame_with_boxes


def process_video(video_path, models, output_dir='detection_results'):
    """Process entire video with all detection models"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🎬 Processing Video: {video_path}")
    print("=" * 70)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"📊 Video Info:")
    print(f"   Duration: {total_frames / fps:.1f} seconds")
    print(f"   Total Frames: {total_frames}")
    print(f"   FPS: {fps}")
    print(f"   Resolution: {width}x{height}")
    
    # Setup output video
    output_video = os.path.join(output_dir, 'detected_video.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    # Statistics
    stats = defaultdict(int)
    frame_detections = []
    
    frame_count = 0
    
    print(f"\n🔍 Running Detection Models...")
    print("Progress: ", end="", flush=True)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Show progress every 10 frames
        if frame_count % max(1, total_frames // 20) == 0:
            print(f"{int(100 * frame_count / total_frames)}%...", end="", flush=True)
        
        # Run all detections
        detections = run_all_detections(frame, models, confidence_threshold=0.4)
        
        # Update statistics
        stats['persons'] += len(detections['persons'])
        stats['weapons'] += len(detections['weapons'])
        stats['suspicious'] += len(detections['suspicious'])
        stats['total_objects'] += len(detections['all_objects'])
        
        # Store frame detection data
        frame_data = {
            'frame_number': frame_count,
            'timestamp': frame_count / fps,
            'detections': {
                'persons': len(detections['persons']),
                'weapons': len(detections['weapons']),
                'suspicious_activities': len(detections['suspicious']),
                'total_objects': len(detections['all_objects']),
            }
        }
        frame_detections.append(frame_data)
        
        # Draw all detections
        annotated_frame = draw_detections(frame, detections)
        
        # Add title and stats to frame
        cv2.putText(annotated_frame, f"Frame: {frame_count}/{total_frames}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated_frame, 
                   f"People: {len(detections['persons'])} | Weapons: {len(detections['weapons'])} | Suspicious: {len(detections['suspicious'])}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Write annotated frame to output video
        out.write(annotated_frame)
    
    cap.release()
    out.release()
    
    print(f"✅ Complete!\n")
    
    # Generate report
    print("\n📊 Detection Results Summary")
    print("=" * 70)
    print(f"✅ Output video saved: {output_video}")
    print(f"\n📈 Total Detections:")
    print(f"   👤 Persons Found: {stats['persons']}")
    print(f"   🔫 Weapons Detected: {stats['weapons']}")
    print(f"   ⚠️  Suspicious Activities: {stats['suspicious']}")
    print(f"   📦 Total Objects: {stats['total_objects']}")
    
    # Save detailed report
    report = {
        'video_file': video_path,
        'processed_at': datetime.now().isoformat(),
        'video_info': {
            'total_frames': total_frames,
            'fps': fps,
            'duration_seconds': total_frames / fps,
            'resolution': f"{width}x{height}",
        },
        'summary': {
            'persons_found': stats['persons'],
            'weapons_detected': stats['weapons'],
            'suspicious_activities': stats['suspicious'],
            'total_objects': stats['total_objects'],
        },
        'frame_by_frame': frame_detections,
    }
    
    report_path = os.path.join(output_dir, 'detection_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved: {report_path}")
    print(f"📁 All results in: {output_dir}")
    print("=" * 70)


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("🎬 RAKSHNETRA - COMPREHENSIVE VIDEO DETECTION")
    print("=" * 70)
    
    # Get video path from command line or use default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Default path
        video_path = r"C:\Users\agast\Downloads\President Droupadi Murmu Reviews International Fleet _ Visakhapatnam Naval Event.mp4"
    
    # Load all models
    models = load_all_models()
    
    if not models:
        print("❌ No models loaded. Cannot proceed.")
        return
    
    # Process video
    process_video(video_path, models)


if __name__ == '__main__':
    main()
