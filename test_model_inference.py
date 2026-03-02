#!/usr/bin/env python
"""Test loading the uploaded model and running a single inference pass.
This script will:
- Check PyTorch availability
- Attempt to load 'media/models/best5.pt'
- Capture memory/CPU before and after load
- Run a single inference pass on a resized dummy frame
- Print exceptions and timing

Run: python test_model_inference.py
"""
import os
import time
import sys

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'media', 'models', 'best5.pt')

print('\n--- Model Inference Diagnostic ---')
print('Model path:', MODEL_PATH)

try:
    import psutil
except Exception:
    psutil = None

try:
    if psutil:
        vm = psutil.virtual_memory()
        print(f'Before: RAM used {vm.percent}%, available {vm.available / (1024**2):.0f} MB')

    import cv2
    import numpy as np

    try:
        import torch
        print('PyTorch found, version:', torch.__version__)
    except Exception as e:
        print('PyTorch not available:', e)
        print('If you want to run .pt models, install torch in your environment.')
        sys.exit(0)

    if not os.path.exists(MODEL_PATH):
        print('Model file not found at path. Check the uploaded file name; listing media/models:')
        for f in os.listdir(os.path.join(os.path.dirname(__file__), 'media', 'models')):
            print(' -', f)
        sys.exit(1)

    t0 = time.time()
    print('\nLoading model...')
    try:
        # Try common load patterns: try torch.load then try torch.hub.load or attempt to instantiate
        loaded = None
        try:
            loaded = torch.load(MODEL_PATH, map_location='cpu')
            print('torch.load returned object of type:', type(loaded))
        except Exception as e_load:
            print('torch.load failed:', e_load)
        
        # Try YOLO/Ultralytics style load via hub (if available)
        if loaded is None:
            try:
                model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, force_reload=False)
                loaded = model
                print('Loaded via torch.hub ultralytics/yolov5')
            except Exception as e_hub:
                print('torch.hub load failed:', e_hub)

        if loaded is None:
            print('Could not load model with heuristics; it may be saved as state_dict or require a specific loader.')
            sys.exit(2)

        load_time = time.time() - t0
        print(f'Loaded model in {load_time:.2f}s')

        if psutil:
            vm = psutil.virtual_memory()
            print(f'After load: RAM used {vm.percent}%, available {vm.available / (1024**2):.0f} MB')

        # Prepare a dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # If loaded has a `.eval` or callable interface, attempt a run
        print('\nRunning a single inference pass...')
        inf_t0 = time.time()
        try:
            # Try common ultralytics/torch model interfaces
            if hasattr(loaded, 'eval') and hasattr(loaded, 'to'):
                loaded.eval()
                # Some YOLO models expect RGB images as list or torch tensor
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Try passing as [img]
                try:
                    res = loaded([img])
                    print('Inference result type:', type(res))
                    # If result has .xyxy or .pandas style, print a brief summary
                    try:
                        if hasattr(res, 'xyxy'):
                            print('res.xyxy length:', len(res.xyxy))
                    except Exception:
                        pass
                except Exception as e_call:
                    print('Calling loaded([img]) failed:', e_call)
                    # Try using detect via forward
                    try:
                        inp = torch.from_numpy(img).permute(2,0,1).unsqueeze(0).float()/255.0
                        with torch.no_grad():
                            out = loaded(inp)
                        print('Inference via tensor forward returned type:', type(out))
                    except Exception as e2:
                        print('Tensor forward failed:', e2)
            else:
                # If loaded is a state_dict, print its keys
                if isinstance(loaded, dict):
                    print('Model appears to be a state_dict with keys (sample):', list(loaded.keys())[:10])
                else:
                    print('Loaded model object of type', type(loaded), 'does not have a standard inference interface.');
        except Exception as e_inf:
            print('Inference attempt raised exception:', e_inf)
        inf_time = time.time() - inf_t0
        print(f'Inference attempt time: {inf_time:.2f}s')

    except Exception as e:
        print('Error loading/running model:', repr(e))
        sys.exit(3)

except Exception as e_outer:
    print('Fatal error in diagnostic script:', repr(e_outer))
    sys.exit(4)

print('\n--- Diagnostic complete ---')
