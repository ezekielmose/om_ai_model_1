from ai_vision.object_detector import analyze_scene_objects
import requests
import base64
import cv2
import json


def encode_frame(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def pick_diverse_frames(frames, num=5):
    if len(frames) <= num:
        return frames

    step = len(frames) // num
    return [frames[i] for i in range(0, len(frames), step)][:num]


# ===============================
# 🧠 MAIN ANALYSIS
# ===============================
def analyze_scene(frames):

    selected_frames = pick_diverse_frames(frames, 5)

    # 🔥 REAL OBJECT DETECTION (NO LLaVA DEPENDENCY)
    yolo_result = analyze_scene_objects(selected_frames)

    images = [encode_frame(f) for f in selected_frames]

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

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload
        )

        result = response.json()
        text = result.get("response", "").strip()

        try:
            parsed = json.loads(text)
        except:
            parsed = {
                "analysis": text,
                "quality_rating": 3
            }

        # 🔥 FORCE OBJECT DATA INTO RESULT
        parsed["hotel_elements"] = yolo_result["hotel_elements"]
        parsed["has_hotel"] = yolo_result["has_hotel"]

        return parsed

    except Exception as e:
        return {
            "analysis": "error",
            "quality_rating": 0,
            "hotel_elements": [],
            "has_hotel": False,
            "issues": [str(e)]
        }
