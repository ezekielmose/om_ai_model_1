# ===============================
# 🔐 SAFE IMPORTS
# ===============================
from ai_vision.object_detector import analyze_scene_objects
import requests
import base64
import json


def get_cv2():
    try:
        import cv2
        return cv2
    except Exception as e:
        raise ImportError(f"OpenCV failed to load: {e}")


# ===============================
# 🖼 ENCODE FRAME SAFELY
# ===============================
def encode_frame(frame):
    try:
        cv2 = get_cv2()
        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            return None

        return base64.b64encode(buffer).decode("utf-8")

    except Exception as e:
        print("⚠️ Frame encoding failed:", e)
        return None


# ===============================
# 🎞 FRAME SAMPLING
# ===============================
def pick_diverse_frames(frames, num=5):
    if not frames:
        return []

    if len(frames) <= num:
        return frames

    step = max(1, len(frames) // num)
    return [frames[i] for i in range(0, len(frames), step)][:num]


# ===============================
# 🧠 MAIN ANALYSIS
# ===============================
def analyze_scene(frames):

    if not frames:
        return {
            "analysis": "no frames provided",
            "quality_rating": 0,
            "hotel_elements": [],
            "has_hotel": False
        }

    selected_frames = pick_diverse_frames(frames, 5)

    # ===============================
    # 🤖 YOLO OBJECT DETECTION (SAFE)
    # ===============================
    try:
        yolo_result = analyze_scene_objects(selected_frames)
    except Exception as e:
        print("⚠️ YOLO analysis failed:", e)
        yolo_result = {
            "hotel_elements": [],
            "has_hotel": False
        }

    # ===============================
    # 🖼 ENCODE IMAGES (SAFE)
    # ===============================
    images = []
    for f in selected_frames:
        encoded = encode_frame(f)
        if encoded:
            images.append(encoded)

    # ===============================
    # 🧠 PROMPT
    # ===============================
    prompt = """
You are a hotel scene analyzer.

You will receive detected objects from a vision system.

Your job:
- describe hotel experience
- evaluate quality
- confirm if experience is immersive

OUTPUT JSON:
{
  "analysis": "...",
  "quality_rating": 0-5
}
"""

    payload = {
        "model": "llava:13b",
        "prompt": prompt + "\nDetected objects: " + str(yolo_result["hotel_elements"]),
        "images": images,
        "stream": False,
        "options": {"temperature": 0.1}
    }

    # ===============================
    # 🌐 API CALL (SAFE)
    # ===============================
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )

        result = response.json()
        text = result.get("response", "").strip()

        try:
            parsed = json.loads(text)
        except Exception:
            parsed = {
                "analysis": text,
                "quality_rating": 3
            }

        # attach detection results
        parsed["hotel_elements"] = yolo_result["hotel_elements"]
        parsed["has_hotel"] = yolo_result["has_hotel"]

        return parsed

    except Exception as e:
        print("⚠️ Vision API failed:", e)

        return {
            "analysis": "AI service unavailable",
            "quality_rating": 0,
            "hotel_elements": yolo_result["hotel_elements"],
            "has_hotel": yolo_result["has_hotel"],
            "issues": [str(e)]
        }
