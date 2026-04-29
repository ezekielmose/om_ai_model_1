import cv2

# fallback safety (prevents silent crashes in some builds)
if cv2.__version__ is None:
    raise ImportError("OpenCV failed to load correctly")

# ===============================
# 🎯 FRAME QUALITY CHECKS
# ===============================
def is_blurry(frame, threshold=100):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold


def is_too_dark(frame, threshold=40):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray.mean() < threshold


# ===============================
# 🎯 SMART FRAME SAMPLING
# ===============================
def sample_scene_frames(scene_frames, max_frames=3):
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

        if not is_blurry(frame) and not is_too_dark(frame):
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

    cap = cv2.VideoCapture(video_path)

    scenes = []
    current_scene = []

    prev_frame = None
    frame_count = 0

    # ===============================
    # 🔧 TUNING PARAMETERS
    # ===============================
    SCENE_THRESHOLD = 18        # sensitivity (lower = more splits)
    MIN_SCENE_LENGTH = 15       # 🔥 prevents micro-scenes
    MAX_SCENE_LENGTH = 120      # prevents overly long scenes
    FRAME_SKIP = 3              # 🔥 reduces noise (process every 3rd frame)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # 🔥 skip frames to reduce sensitivity
        if frame_count % FRAME_SKIP != 0:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray).mean()

            # 🎬 Scene change logic (FIXED)
            if (
                (diff > SCENE_THRESHOLD and len(current_scene) > MIN_SCENE_LENGTH)
                or len(current_scene) >= MAX_SCENE_LENGTH
            ):
                if current_scene:
                    sampled = sample_scene_frames(current_scene)
                    scenes.append(sampled)

                current_scene = []

        current_scene.append(frame)
        prev_frame = gray

    # 🎬 Handle last scene
    if current_scene:
        sampled = sample_scene_frames(current_scene)
        scenes.append(sampled)

    cap.release()

    return scenes
