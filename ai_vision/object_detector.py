from ultralytics import YOLO
import cv2


# ===============================
# 🤖 LOAD MODEL
# ===============================
model = YOLO("yolov8n.pt")  # lightweight model (fast)


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
def detect_objects(frame, conf_threshold=0.4):

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

    scene_objects = []

    for frame in frames:
        objects = detect_objects(frame)
        scene_objects.extend(objects)

    # remove duplicates
    scene_objects = list(set(scene_objects))

    return {
        "hotel_elements": scene_objects,
        "has_hotel": len(scene_objects) > 0
    }
