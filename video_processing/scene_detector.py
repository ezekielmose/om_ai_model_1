# ===============================
# 🔐 SAFE OPENCV IMPORT (LAZY LOAD)
# ===============================
def get_cv2():
    try:
        import cv2
        return cv2
    except Exception as e:
        raise ImportError(f"OpenCV failed to load: {e}")


# ===============================
# 🎯 FRAME QUALITY CHECKS
# ===============================
def is_blurry(frame, cv2, threshold=100):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold


def is_too_dark(frame, cv2, threshold=40):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray.mean() < threshold


# ===============================
# 🎯 SMART FRAME SAMPLING
# ===============================
def sample_scene_frames(scene_frames, cv2, max_frames=3):
    """
    Select best frames from a scene:
    - evenly spaced
    - not blurry
    - not too dark
    """

    if not scene_frames:
        return []

    step = max(1, len(scene_frames) // max_frames)
    selected = []

    for i in range(0, len(scene_frames), step):
        frame = scene_frames[i]

        if not is_blurry(frame, cv2) and not is_too_dark(frame, cv2):
            selected.append(frame)

        if len(selected) >= max_frames:
            break

    # fallback if all frames were filtered out
    if not selected:
        selected = scene_frames[:max_frames]

    return selected


# ===============================
# 🎥 MAIN SCENE EXTRACTION
# ===============================
def extract_scenes(video_path):
    try:
        cv2 = get_cv2()
    except Exception as e:
        print("⚠️ OpenCV not available, skipping scene detection:", e)
        return []  # graceful fallback

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("⚠️ Failed to open video")
        return []

    scenes = []
    current_scene = []

    prev_frame = None
    frame_count = 0

    # ===============================
    # 🔧 TUNING PARAMETERS
    # ===============================
    SCENE_THRESHOLD = 18
    MIN_SCENE_LENGTH = 15
    MAX_SCENE_LENGTH = 120
    FRAME_SKIP = 3

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # skip frames
        if frame_count % FRAME_SKIP != 0:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray).mean()

            # scene change logic
            if (
                (diff > SCENE_THRESHOLD and len(current_scene) > MIN_SCENE_LENGTH)
                or len(current_scene) >= MAX_SCENE_LENGTH
            ):
                if current_scene:
                    sampled = sample_scene_frames(current_scene, cv2)
                    scenes.append(sampled)

                current_scene = []

        current_scene.append(frame)
        prev_frame = gray

    # handle last scene
    if current_scene:
        sampled = sample_scene_frames(current_scene, cv2)
        scenes.append(sampled)

    cap.release()

    return scenes
