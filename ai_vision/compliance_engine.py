# ===============================
# 🔐 SAFE (LAZY) IMPORTS
# ===============================
def get_cv2():
    try:
        import cv2
        return cv2
    except Exception as e:
        raise ImportError(f"OpenCV failed to load: {e}")


def get_numpy():
    try:
        import numpy as np
        return np
    except Exception as e:
        raise ImportError(f"NumPy failed to load: {e}")


def get_pytesseract():
    try:
        import pytesseract
        return pytesseract
    except Exception as e:
        raise ImportError(f"Tesseract failed to load: {e}")


# ===============================
# 📊 FRAME QUALITY CHECK
# ===============================
def analyze_frame_quality(frame, cv2, np):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)

    return {
        "blur_score": blur_score,
        "brightness": brightness
    }


# ===============================
# 🧠 OCR TEXT DETECTION
# ===============================
def detect_text_overlays(frame, cv2, pytesseract):
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return len(text.strip()) > 5
    except Exception:
        return False  # fallback if OCR fails


# ===============================
# 🎞 MOTION DETECTION
# ===============================
def detect_static_frames(prev_frame, current_frame, cv2, np):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(prev_gray, curr_gray)
    motion_score = np.mean(diff)

    return motion_score


# ===============================
# 🚨 HARD FAIL GATE
# ===============================
def apply_hard_fail_gate(score, issues):
    critical_failures = [
        "text_overlay_detected",
        "watermark",
        "logo",
        "branding",
        "not_vertical_9_16",
        "shaky_or_blurry_video",
        "blank_frame",
        "static_images_detected"
    ]

    if any(issue in issues for issue in critical_failures):
        return min(score, 2.5)

    return score


# ===============================
# 🎥 VIDEO COMPLIANCE ANALYZER
# ===============================
def analyze_video_compliance(video_path):

    # 🔐 load dependencies safely
    try:
        cv2 = get_cv2()
        np = get_numpy()
    except Exception as e:
        print("⚠️ Core CV dependencies missing:", e)
        return {"score": 0, "issues": ["cv_dependencies_failed"]}

    try:
        pytesseract = get_pytesseract()
    except Exception as e:
        print("⚠️ OCR unavailable:", e)
        pytesseract = None  # allow fallback

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            "score": 0,
            "issues": ["video_not_openable"]
        }

    frame_count = 0
    blur_values = []
    brightness_values = []
    issues = []

    has_text_overlay = False
    prev_frame = None
    low_motion_count = 0

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    vertical_ratio = height / width if width != 0 else 0

    # ===============================
    # 🎞 FRAME SAMPLING LOOP
    # ===============================
    while frame_count < 30:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            metrics = analyze_frame_quality(frame, cv2, np)
            blur_values.append(metrics["blur_score"])
            brightness_values.append(metrics["brightness"])

            # OCR (only if available)
            if pytesseract and detect_text_overlays(frame, cv2, pytesseract):
                has_text_overlay = True

            # motion detection
            if prev_frame is not None:
                motion = detect_static_frames(prev_frame, frame, cv2, np)
                if motion < 2:
                    low_motion_count += 1

        except Exception as e:
            print("⚠️ Frame processing error:", e)

        prev_frame = frame
        frame_count += 1

    cap.release()

    avg_blur = np.mean(blur_values) if blur_values else 0
    avg_brightness = np.mean(brightness_values) if brightness_values else 0

    # ===============================
    # ❌ QUALITY RULES
    # ===============================
    if avg_blur < 80:
        issues.append("shaky_or_blurry_video")

    if avg_brightness > 240:
        issues.append("overexposed_video")

    if avg_brightness < 40:
        issues.append("too_dark_video")

    # ===============================
    # ❌ STRUCTURE RULES
    # ===============================
    if vertical_ratio < 1.2:
        issues.append("not_vertical_9_16")

    # ===============================
    # ❌ OCR RULE
    # ===============================
    if has_text_overlay:
        issues.append("text_overlay_detected")

    # ===============================
    # ❌ STATIC IMAGE RULE
    # ===============================
    if low_motion_count > 10:
        issues.append("static_images_detected")

    # ===============================
    # BASE SCORE
    # ===============================
    score = 5

    if "shaky_or_blurry_video" in issues:
        score -= 1.5

    if "overexposed_video" in issues:
        score -= 1

    if "too_dark_video" in issues:
        score -= 1

    if "not_vertical_9_16" in issues:
        score -= 2

    if "text_overlay_detected" in issues:
        score = min(score, 2.5)

    if "static_images_detected" in issues:
        score = 0

    # ===============================
    # 🚨 HARD FAIL GATE
    # ===============================
    score = apply_hard_fail_gate(score, issues)
    score = max(0, min(5, score))

    return {
        "score": round(score, 2),
        "issues": issues
    }
