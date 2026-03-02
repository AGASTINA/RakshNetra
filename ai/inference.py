"""AI Model Inference Engine
Handles loading and running inference on various model formats (.pt, ONNX, etc.)
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import numpy as np
import cv2

logger = logging.getLogger(__name__)


class ModelInferenceEngine:
    """Manages model loading and inference execution"""

    _loaded_models: Dict[str, Any] = {}
    _face_cache_loaded_at: Dict[str, float] = {}
    _face_cache_entries: Dict[str, List[Dict[str, Any]]] = {}
    _facenet_model: Optional[object] = None
    _facenet_detector: Optional[object] = None

    @classmethod
    def load_model(cls, model_path: str, model_type: str) -> Optional[object]:
        """Load an AI model from file.

        Returns the loaded model object or None on failure.
        """
        if model_path in cls._loaded_models:
            logger.info("Using cached model: %s", model_path)
            return cls._loaded_models[model_path]

        if not os.path.exists(model_path):
            logger.error("Model file not found: %s", model_path)
            return None

        try:
            ext = Path(model_path).suffix.lower()

            if ext == ".pt":
                # PyTorch / YOLO model
                try:
                    try:
                        from ultralytics import YOLO  # type: ignore

                        logger.info("Loading YOLO model from %s", model_path)
                        model = YOLO(model_path)
                        cls._loaded_models[model_path] = model
                        return model
                    except Exception as e:
                        logger.warning("YOLO load failed, falling back to torch.load: %s", e)

                    import torch  # type: ignore

                    logger.info("Loading PyTorch model from %s", model_path)
                    try:
                        model = torch.jit.load(model_path, map_location="cpu")
                    except Exception:
                        model = torch.load(model_path, map_location="cpu")
                    try:
                        model.eval()
                    except Exception:
                        pass
                    cls._loaded_models[model_path] = model
                    return model
                except ImportError:
                    logger.error("PyTorch/Ultralytics not installed")
                    return None

            elif ext == ".onnx":
                # ONNX model
                try:
                    import onnxruntime as ort  # type: ignore

                    logger.info("Loading ONNX model from %s", model_path)
                    sess = ort.InferenceSession(model_path)
                    cls._loaded_models[model_path] = sess
                    return sess
                except ImportError:
                    logger.error("ONNX Runtime not installed")
                    return None

            else:
                logger.warning("Unsupported model format: %s", ext)
                return None

        except Exception as e:
            logger.exception("Error loading model %s: %s", model_path, e)
            return None

    @classmethod
    def run_inference(
        cls,
        model: object,
        frame: np.ndarray,
        model_type: str,
        confidence_threshold: float = 0.5,
        source_shape: Optional[Tuple[int, int, int]] = None,
    ) -> Dict[str, Any]:
        """Run inference on a frame.

        This is a placeholder implementation: replace with model-specific logic.
        """
        if model is None and model_type != "face_recognition":
            return {"detections": [], "error": "Model not loaded"}

        try:
            logger.info("Running %s inference on frame shape %s", model_type, getattr(frame, "shape", None))

            # Face recognition (database-backed)
            if model_type == "face_recognition":
                backend = cls._get_face_backend()
                if backend == "facenet":
                    return cls._run_facenet_inference(frame, source_shape)
                return cls._run_face_recognition_inference(frame, source_shape)

            # Ultralytics YOLO
            if hasattr(model, "predict"):
                results = model.predict(source=frame, conf=confidence_threshold, verbose=False)
                detections = []
                for result in results:
                    names = getattr(result, "names", {}) or {}
                    boxes = getattr(result, "boxes", None)
                    if boxes is None:
                        continue
                    for box in boxes:
                        xyxy = box.xyxy[0].tolist() if hasattr(box, "xyxy") else []
                        conf = float(box.conf[0]) if hasattr(box, "conf") else 0.0
                        cls_id = int(box.cls[0]) if hasattr(box, "cls") else -1
                        label = names.get(cls_id, "Object") if isinstance(names, dict) else "Object"
                        if xyxy:
                            detection = {
                                "bbox": xyxy,
                                "confidence": conf,
                                "label": label
                            }
                            if source_shape is not None:
                                detection["source_shape"] = source_shape
                                detection["inference_shape"] = getattr(frame, "shape", None)
                            detections.append(detection)
                return {
                    "model_type": model_type,
                    "detections": detections,
                    "frame_shape": getattr(frame, "shape", None),
                    "threshold": confidence_threshold,
                    "status": "inference_complete",
                }

            # Unknown model type
            return {
                "model_type": model_type,
                "detections": [],
                "frame_shape": getattr(frame, "shape", None),
                "threshold": confidence_threshold,
                "status": "unsupported_model",
            }

        except Exception as e:
            logger.exception("Inference error: %s", e)
            return {"detections": [], "error": str(e)}

    @classmethod
    def clear_cache(cls) -> None:
        """Clear model cache."""
        cls._loaded_models.clear()
        cls._face_cache_entries = {}
        cls._face_cache_loaded_at = {}
        logger.info("Model cache cleared")

    @classmethod
    def _get_face_cache_ttl(cls) -> float:
        try:
            from django.conf import settings

            return float(getattr(settings, "FACE_RECOGNITION_CACHE_TTL", 30.0))
        except Exception:
            return 30.0

    @classmethod
    def _get_face_match_threshold(cls) -> float:
        try:
            from django.conf import settings

            return float(getattr(settings, "FACE_RECOGNITION_THRESHOLD", 0.55))
        except Exception:
            return 0.55

    @classmethod
    def _get_facenet_cosine_threshold(cls) -> float:
        try:
            from django.conf import settings

            return float(getattr(settings, "FACE_RECOGNITION_COSINE_THRESHOLD", 0.6))
        except Exception:
            return 0.6

    @classmethod
    def _get_face_backend(cls) -> str:
        try:
            from django.conf import settings

            return str(getattr(settings, "FACE_RECOGNITION_BACKEND", "facenet")).strip().lower()
        except Exception:
            return "facenet"

    @classmethod
    def _load_face_database(cls, backend: str, recognizer: Optional[object] = None, detector: Optional[object] = None) -> List[Dict[str, Any]]:
        """Load face encodings from FaceIdentity records with caching."""
        cache_ttl = cls._get_face_cache_ttl()
        now = time.time()
        last_loaded = cls._face_cache_loaded_at.get(backend, 0.0)
        cached_entries = cls._face_cache_entries.get(backend, [])
        if cached_entries and (now - last_loaded) < cache_ttl:
            return cached_entries

        try:
            from ai.models import FaceIdentity
        except Exception as e:
            logger.error("Failed to import FaceIdentity: %s", e)
            return []

        entries: List[Dict[str, Any]] = []
        for face in FaceIdentity.objects.all():
            if not face.face_image:
                continue
            try:
                img_path = face.face_image.path
            except Exception:
                continue
            if not img_path or not os.path.exists(img_path):
                continue
            try:
                if backend == "facenet":
                    from PIL import Image

                    if detector is None or recognizer is None:
                        continue
                    image = Image.open(img_path).convert("RGB")
                    face_tensor = detector(image)
                    if face_tensor is None:
                        continue
                    if len(face_tensor.shape) == 3:
                        face_tensor = face_tensor.unsqueeze(0)
                    embeddings = recognizer(face_tensor).detach().cpu().numpy()
                    for embedding in embeddings:
                        entries.append({
                            "encoding": embedding,
                            "label": face.label,
                            "identity_type": face.identity_type,
                            "position": face.position,
                            "description": face.description,
                        })
                else:
                    if recognizer is None:
                        continue
                    image = recognizer.load_image_file(img_path)
                    encodings = recognizer.face_encodings(image)
                    if not encodings:
                        continue
                    for encoding in encodings:
                        entries.append({
                            "encoding": encoding,
                            "label": face.label,
                            "identity_type": face.identity_type,
                            "position": face.position,
                            "description": face.description,
                        })
            except Exception as e:
                logger.warning("Failed to encode face %s: %s", face.label, e)

        cls._face_cache_entries[backend] = entries
        cls._face_cache_loaded_at[backend] = now
        return entries

    @classmethod
    def _run_face_recognition_inference(
        cls,
        frame: np.ndarray,
        source_shape: Optional[Tuple[int, int, int]] = None,
    ) -> Dict[str, Any]:
        try:
            import face_recognition  # type: ignore
        except Exception:
            logger.warning("face_recognition package not installed; skipping face recognition")
            return {
                "model_type": "face_recognition",
                "detections": [],
                "frame_shape": getattr(frame, "shape", None),
                "threshold": cls._get_face_match_threshold(),
                "status": "face_recognition_unavailable",
            }

        known_entries = cls._load_face_database("face_recognition", recognizer=face_recognition)
        known_encodings = [entry["encoding"] for entry in known_entries]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        detections = []
        match_threshold = cls._get_face_match_threshold()

        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            label = "Unknown"
            identity_type = "unknown"
            confidence = 0.0
            position = ""

            if known_encodings:
                distances = face_recognition.face_distance(known_encodings, encoding)
                if len(distances) > 0:
                    best_idx = int(np.argmin(distances))
                    best_distance = float(distances[best_idx])
                    if best_distance <= match_threshold:
                        best_entry = known_entries[best_idx]
                        label = best_entry.get("label", label)
                        identity_type = best_entry.get("identity_type", identity_type)
                        position = best_entry.get("position", "")
                        confidence = max(0.0, 1.0 - best_distance)

            detection = {
                "bbox": [left, top, right, bottom],
                "confidence": confidence,
                "label": label,
                "identity_type": identity_type,
                "position": position,
            }
            if source_shape is not None:
                detection["source_shape"] = source_shape
                detection["inference_shape"] = getattr(frame, "shape", None)
            detections.append(detection)

        return {
            "model_type": "face_recognition",
            "detections": detections,
            "frame_shape": getattr(frame, "shape", None),
            "threshold": match_threshold,
            "status": "inference_complete",
        }

    @classmethod
    def _get_facenet_components(cls) -> Tuple[Optional[object], Optional[object]]:
        if cls._facenet_model is not None and cls._facenet_detector is not None:
            return cls._facenet_model, cls._facenet_detector

        try:
            from facenet_pytorch import MTCNN, InceptionResnetV1  # type: ignore

            cls._facenet_detector = MTCNN(image_size=160, margin=20, keep_all=True)
            cls._facenet_model = InceptionResnetV1(pretrained='vggface2').eval()
            return cls._facenet_model, cls._facenet_detector
        except Exception as e:
            logger.warning("Failed to initialize facenet components: %s", e)
            return None, None

    @classmethod
    def _run_facenet_inference(
        cls,
        frame: np.ndarray,
        source_shape: Optional[Tuple[int, int, int]] = None,
    ) -> Dict[str, Any]:
        model, detector = cls._get_facenet_components()
        if model is None or detector is None:
            return {
                "model_type": "face_recognition",
                "detections": [],
                "frame_shape": getattr(frame, "shape", None),
                "threshold": cls._get_facenet_cosine_threshold(),
                "status": "facenet_unavailable",
            }

        known_entries = cls._load_face_database("facenet", recognizer=model, detector=detector)
        known_embeddings = [entry["encoding"] for entry in known_entries]

        try:
            from PIL import Image
        except Exception:
            logger.warning("Pillow not installed; facenet requires Pillow")
            return {
                "model_type": "face_recognition",
                "detections": [],
                "frame_shape": getattr(frame, "shape", None),
                "threshold": cls._get_facenet_cosine_threshold(),
                "status": "facenet_unavailable",
            }

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        boxes, _ = detector.detect(pil_image)

        detections = []
        if boxes is None:
            return {
                "model_type": "face_recognition",
                "detections": detections,
                "frame_shape": getattr(frame, "shape", None),
                "threshold": cls._get_facenet_cosine_threshold(),
                "status": "inference_complete",
            }

        face_tensors = detector(pil_image)
        if face_tensors is None:
            return {
                "model_type": "face_recognition",
                "detections": detections,
                "frame_shape": getattr(frame, "shape", None),
                "threshold": cls._get_facenet_cosine_threshold(),
                "status": "inference_complete",
            }

        if len(face_tensors.shape) == 3:
            face_tensors = face_tensors.unsqueeze(0)

        embeddings = model(face_tensors).detach().cpu().numpy()
        threshold = cls._get_facenet_cosine_threshold()

        for box, embedding in zip(boxes, embeddings):
            left, top, right, bottom = [float(v) for v in box]
            label = "Unknown"
            identity_type = "unknown"
            position = ""
            confidence = 0.0

            if known_embeddings:
                similarities = cls._cosine_similarity(np.array(known_embeddings), embedding)
                best_idx = int(np.argmax(similarities))
                best_score = float(similarities[best_idx])
                if best_score >= threshold:
                    best_entry = known_entries[best_idx]
                    label = best_entry.get("label", label)
                    identity_type = best_entry.get("identity_type", identity_type)
                    position = best_entry.get("position", "")
                    confidence = best_score

            detection = {
                "bbox": [left, top, right, bottom],
                "confidence": confidence,
                "label": label,
                "identity_type": identity_type,
                "position": position,
            }
            if source_shape is not None:
                detection["source_shape"] = source_shape
                detection["inference_shape"] = getattr(frame, "shape", None)
            detections.append(detection)

        return {
            "model_type": "face_recognition",
            "detections": detections,
            "frame_shape": getattr(frame, "shape", None),
            "threshold": threshold,
            "status": "inference_complete",
        }

    @staticmethod
    def _cosine_similarity(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
        if matrix.size == 0:
            return np.array([])
        denom = (np.linalg.norm(matrix, axis=1) * np.linalg.norm(vector)) + 1e-8
        return (matrix @ vector) / denom


class FrameProcessor:
    """Processes video frames and applies AI models"""

    @staticmethod
    def preprocess_frame(frame: np.ndarray, target_size: Tuple[int, int] = (640, 640)) -> np.ndarray:
        """Resize and normalize frame for model input.

        `target_size` is (width, height) to match OpenCV's ordering.
        """
        try:
            resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
            normalized = resized.astype(np.float32) / 255.0
            return normalized
        except Exception as e:
            logger.exception("Frame preprocessing error: %s", e)
            return frame

    @staticmethod
    def draw_detections(frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Draw detection boxes and labels onto the frame."""
        try:
            annotated_frame = frame.copy()

            for detection in detections:
                bbox = detection.get("bbox")
                if bbox and len(bbox) >= 4:
                    try:
                        x1, y1, x2, y2 = map(float, bbox[:4])
                    except Exception:
                        continue

                    confidence = float(detection.get("confidence", 0.0))
                    identity_type = detection.get("identity_type")
                    if not identity_type:
                        label_hint = str(detection.get("label", "")).lower()
                        if label_hint in {"unknown", "suspect"}:
                            identity_type = label_hint

                    if identity_type in {"suspect", "unknown"}:
                        color = (0, 0, 255)
                    elif identity_type:
                        color = (0, 255, 0)
                    else:
                        color = (0, 255, 0) if confidence > 0.7 else (0, 165, 255)

                    source_shape = detection.get("source_shape")
                    inference_shape = detection.get("inference_shape")
                    if (
                        source_shape
                        and inference_shape
                        and len(source_shape) >= 2
                        and len(inference_shape) >= 2
                        and (source_shape[0] != inference_shape[0] or source_shape[1] != inference_shape[1])
                    ):
                        try:
                            scale_x = float(source_shape[1]) / float(inference_shape[1])
                            scale_y = float(source_shape[0]) / float(inference_shape[0])
                            x1, x2 = x1 * scale_x, x2 * scale_x
                            y1, y2 = y1 * scale_y, y2 * scale_y
                        except Exception:
                            pass

                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                    label_txt = f"{detection.get('label', 'Object')}"
                    position = str(detection.get("position") or "").strip()
                    if position:
                        label_txt = f"{label_txt} - {position}"
                    if identity_type:
                        label_txt = f"{label_txt} [{identity_type}]"
                    label_txt = f"{label_txt} {confidence:.2f}"
                    cv2.putText(
                        annotated_frame,
                        label_txt,
                        (x1, max(0, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2,
                    )

            return annotated_frame
        except Exception as e:
            logger.exception("Detection drawing error: %s", e)
            return frame
    @staticmethod
    def detect_fighting(detections: List[Dict[str, Any]], frame_shape: Tuple[int, int, int]) -> List[Dict[str, Any]]:
        """Detect fighting/violence based on people interactions.
        
        Analyzes person bounding boxes for:
        - Multiple people in close proximity
        - Overlapping bounding boxes  
        - Clustered detections indicating grappling/contact
        
        Returns list of fighting detections if conditions are met.
        """
        fighting_detections = []
        
        if not detections or len(detections) < 2:
            return fighting_detections
        
        try:
            # Extract people/person detections (look for 'person', 'player', or high confidence)
            people_bboxes = []
            for det in detections:
                bbox = det.get("bbox", [])
                label = str(det.get("label", "")).lower()
                confidence = float(det.get("confidence", 0.0))
                
                # Include detections that are likely people
                if len(bbox) >= 4 and (
                    "person" in label or
                    "player" in label or
                    "human" in label or
                    confidence > 0.6
                ):
                    people_bboxes.append({
                        "bbox": bbox,
                        "confidence": confidence,
                        "label": det.get("label", "person")
                    })
            
            if len(people_bboxes) < 2:
                return fighting_detections
            
            # Check for overlapping/close bounding boxes
            height, width = frame_shape[:2]
            overlap_threshold = 0.15  # 15% overlap (more sensitive)
            proximity_threshold = 0.25  # 25% of frame width (more sensitive)
            clusters = []
            used = set()
            
            for i, person1 in enumerate(people_bboxes):
                if i in used:
                    continue
                
                cluster = [person1]
                used.add(i)
                
                for j, person2 in enumerate(people_bboxes[i+1:], start=i+1):
                    if j in used:
                        continue
                    
                    # Calculate overlap/proximity
                    box1 = person1["bbox"]
                    box2 = person2["bbox"]
                    
                    x1_min, y1_min, x1_max, y1_max = box1[:4]
                    x2_min, y2_min, x2_max, y2_max = box2[:4]
                    
                    # Calculate intersection
                    inter_x_min = max(x1_min, x2_min)
                    inter_y_min = max(y1_min, y2_min)
                    inter_x_max = min(x1_max, x2_max)
                    inter_y_max = min(y1_max, y2_max)
                    
                    if inter_x_max > inter_x_min and inter_y_max > inter_y_min:
                        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
                        area1 = (x1_max - x1_min) * (y1_max - y1_min)
                        area2 = (x2_max - x2_min) * (y2_max - y2_min)
                        min_area = min(area1, area2)
                        overlap_ratio = inter_area / (min_area + 1e-6)
                        
                        if overlap_ratio > overlap_threshold:
                            cluster.append(person2)
                            used.add(j)
                    else:
                        # Check if boxes are close (distance-based)
                        center1_x = (x1_min + x1_max) / 2
                        center1_y = (y1_min + y1_max) / 2
                        center2_x = (x2_min + x2_max) / 2
                        center2_y = (y2_min + y2_max) / 2
                        
                        # Distance threshold (more sensitive for fighting)
                        distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2) ** 0.5
                        max_distance = width * proximity_threshold
                        
                        # Also check vertical proximity (people at similar heights)
                        height_diff = abs(center1_y - center2_y)
                        vertical_threshold = height * 0.3
                        
                        if distance < max_distance and height_diff < vertical_threshold:
                            cluster.append(person2)
                            used.add(j)
                
                if len(cluster) >= 2:
                    clusters.append(cluster)
            
            # Create fighting detections for clusters with 2+ people
            for cluster in clusters:
                if len(cluster) >= 2:
                    # Calculate cluster bounding box
                    all_bboxes = [p["bbox"] for p in cluster]
                    x_coords = [b[0] for b in all_bboxes] + [b[2] for b in all_bboxes]
                    y_coords = [b[1] for b in all_bboxes] + [b[3] for b in all_bboxes]
                    
                    cluster_bbox = [
                        min(x_coords),
                        min(y_coords),
                        max(x_coords),
                        max(y_coords)
                    ]
                    
                    # Calculate combined confidence
                    avg_confidence = sum(p["confidence"] for p in cluster) / len(cluster)
                    
                    # Higher confidence if more people or higher overlap
                    confidence_boost = 0.2 if len(cluster) >= 3 else 0.15
                    
                    fighting_detection = {
                        "bbox": cluster_bbox,
                        "label": "fight",  # Lowercase for consistency
                        "confidence": min(0.95, avg_confidence + confidence_boost),
                        "people_count": len(cluster),
                        "type": "fighting_violence",
                        "alert_level": "CRITICAL" if len(cluster) >= 3 else "HIGH"
                    }
                    fighting_detections.append(fighting_detection)
            
            return fighting_detections
            
        except Exception as e:
            logger.exception("Fighting detection error: %s", e)
            return fighting_detections