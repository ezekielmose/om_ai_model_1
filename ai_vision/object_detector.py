# ===============================
# 🔐 SAFE (LAZY) IMPORTS
# ===============================
def get_yolo_model():
    try:
        from ultralytics import YOLO
        return YOLO("yolov8n.pt")  # lightweight model
    except Exception as e:
        raise ImportError(f"YOLO failed to load: {e}")


def get_cv2():
    try:
        import cv2
        return cv2
    except Exception as e:
        raise ImportError(f"OpenCV failed to load: {e}")


# ===============================
# 🎯 HOTEL OBJECT MAPPING
# ===============================
HOTEL_OBJECTS = {
    "bed": "room",
    "chair": "room",
    "couch": "room",
    "tv": "room",
    "potted plant": "lobby",
    "sink": "bathroom",
    "toilet": "bathroom",
    "dining table": "dining",
    "person": "ignored",
}


# ===============================
# 🧠 DETECT OBJECTS IN FRAME
# ===============================
def detect_objects(frame, model, conf_threshold=0.4):

    results = model(frame, verbose=False)[0]

    detected = []

    for box in results.boxes.data.tolist():
        cls_id = int(box[5])
        confidence = float(box[4])
        label = results.names[cls_id]

        if confidence < conf_threshold:
            continue

        if label in HOTEL_OBJECTS:
            mapped = HOTEL_OBJECTS[label]
            if mapped != "ignored":
                detected.append(mapped)

    return list(set(detected))


# ===============================
# 🎥 ANALYZE SCENE WITH YOLO
# ===============================
def analyze_scene_objects(frames):

    try:
        model = get_yolo_model()
    except Exception as e:
        print("⚠️ YOLO not available:", e)
        return {
            "hotel_elements": [],
            "has_hotel": False
        }

    scene_objects = []

    for frame in frames:
        try:
            objects = detect_objects(frame, model)
            scene_objects.extend(objects)
        except Exception as e:
            print("⚠️ Frame processing failed:", e)
            continue

    # remove duplicates
    scene_objects = list(set(scene_objects))

    return {
        "hotel_elements": scene_objects,
        "has_hotel": len(scene_objects) > 0
    }
