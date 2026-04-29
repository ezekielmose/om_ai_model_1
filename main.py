import os
from downloader.download_reels import download_reel
from video_processing.scene_detector import extract_scenes
from ai_vision.vision_engine import analyze_scene
from sheets.google_sheets import save_reel_summary
from ai_vision.compliance_engine import analyze_video_compliance
import cv2

# ✅ NEW IMPORTS FOR AIR RESOLVER
import requests
import re
from bs4 import BeautifulSoup


# ===============================
# 🌐 AIR LINK RESOLVER (UNCHANGED)
# ===============================
def resolve_air_link(url):

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)

        soup = BeautifulSoup(r.text, "html.parser")

        for video in soup.find_all("video"):
            if video.get("src"):
                return video["src"]

        for source in soup.find_all("source"):
            if source.get("src") and ".mp4" in source["src"]:
                return source["src"]

        match = re.search(r"https://cdn\.air\.inc[^\s\"']+\.mp4", r.text)
        if match:
            return match.group(0)

        return None

    except Exception as e:
        print(f"Air resolver failed: {e}")
        return None


# ===============================
# 🎥 VIDEO DURATION
# ===============================
def get_video_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    if fps == 0:
        return 0

    return round(frame_count / fps, 2)


# ===============================
# 🧠 SCORING (UPDATED WITH OVERLAY RULES)
# ===============================
def calculate_final_score(scene_results):

    if not scene_results:
        return 0

    score = 5.0

    total_scenes = len(scene_results)

    overlay_hits = 0
    early_overlay = False
    late_overlay = False

    for i, scene in enumerate(scene_results):

        text = scene.get("analysis", "").lower()
        elements = scene.get("hotel_elements", [])

        is_overlay = (
            "watermark" in text or
            "logo" in text or
            "branding" in text or
            "text overlay" in text or
            "caption" in text
        )

        if is_overlay:
            overlay_hits += 1

            if i <= max(1, int(total_scenes * 0.15)):
                early_overlay = True

            if i >= int(total_scenes * 0.85):
                late_overlay = True

        if "watermark" in text or "logo" in text or "branding" in text:
            score -= 2
        if "text overlay" in text or "caption" in text:
            score -= 1.5
        if "horizontal crop" in text:
            score -= 2
        if "shaky" in text or "unstable" in text:
            score -= 1.5
        if "fast cut" in text or "flashy effect" in text:
            score -= 1
        if "time-lapse" in text or "fast forward" in text:
            score -= 2
        if "generic hallway" in text or "empty hallway" in text:
            score -= 1.5
        if "disconnected shots" in text:
            score -= 1.5
        if "third party branding" in text:
            score -= 2
        if "low resolution" in text or "480p" in text:
            score -= 1.5
        if "blurry" in text:
            score -= 1
        if "overexposed" in text:
            score -= 1
        if "grey tone" in text or "dull" in text:
            score -= 1
        if "fade-in" in text or "fade in" in text:
            score -= 1.5
        if "blank frame" in text:
            score -= 2
        if "non-vertical" in text or "horizontal video" in text:
            score -= 2

        if "room" in elements:
            score += 0.4
        if "pool" in elements:
            score += 0.4
        if "lobby" in elements:
            score += 0.3
        if "spa" in elements:
            score += 0.3
        if "dining" in elements:
            score += 0.3
        if "view" in elements:
            score += 0.4

        if "aspirational" in text:
            score += 0.5
        if "smooth camera" in text:
            score += 0.5
        if "strong hook" in text or "first 5 seconds" in text:
            score += 0.5
        if "well lit" in text:
            score += 0.4

    # ===============================
    # ❌ FULL VIDEO TEXT → AUTO REJECT
    # ===============================
    if overlay_hits >= total_scenes * 0.5:
        return 2.0

    final_score = round(max(0, min(5, score)), 2)

    # ===============================
    # ⚖️ START/END TEXT → FORCE 4.0
    # ===============================
    if overlay_hits > 0 and overlay_hits < total_scenes * 0.3:
        if early_overlay or late_overlay:
            final_score = 4.0

    return final_score


# ===============================
# 🔥 SINGLE PIPELINE (UPDATED FIX)
# ===============================
def run_single_pipeline(reel_url):

    if os.path.exists(reel_url):
        video_path = reel_url

    else:

        if "app.air.inc" in reel_url:
            print(f"Resolving Air link: {reel_url}")
            resolved_url = resolve_air_link(reel_url)

            if not resolved_url:
                return {
                    "reel_url": reel_url,
                    "score": 0,
                    "passed": False,
                    "duration": 0,
                    "results": [],
                    "issues": ["Failed to resolve Air video link"],
                    "positives": []
                }

            reel_url = resolved_url

        video_path = download_reel(reel_url)

    scenes = extract_scenes(video_path)

    compliance = analyze_video_compliance(video_path)
    issues = compliance.get("issues", [])

    results = []

    for scene in scenes:

        try:
            analysis = analyze_scene(scene)
            analysis.setdefault("analysis", "")
            analysis.setdefault("hotel_elements", [])
        except Exception:
            analysis = {
                "analysis": "Analysis failed",
                "quality_rating": 0,
                "hotel_elements": [],
                "has_hotel": False
            }

        results.append(analysis)

    content_score = calculate_final_score(results)
    visual_score = compliance["score"]

    final_score = round((content_score * 0.5) + (visual_score * 0.5), 2)

    critical_failures = [
        "text_overlay_detected",
        "watermark",
        "logo",
        "branding",
        "not_vertical_9_16",
        "shaky_or_blurry_video",
        "blank_frame"
    ]

    passed = (
        final_score >= 3 and
        not any(issue in critical_failures for issue in issues)
    )

    duration = get_video_duration(video_path)

    positives = []

    if passed:

        if final_score >= 4:
            positives.append("High overall video quality")
        elif final_score >= 3:
            positives.append("Good overall quality")

        if duration >= 5:
            positives.append("Adequate video duration")

        elements = []
        for r in results:
            elements.extend(r.get("hotel_elements", []))

        unique_elements = list(set(elements))

        if unique_elements:
            positives.append(f"Shows hotel features: {', '.join(unique_elements)}")

        all_text = " ".join([r.get("analysis", "") for r in results]).lower()

        if "smooth" in all_text:
            positives.append("Smooth camera movement")

        if "lighting" in all_text:
            positives.append("Good lighting")

        if "luxury" in all_text:
            positives.append("Luxury feel")

        if not positives:
            positives.append("Meets platform quality standards")

    save_reel_summary(reel_url, duration, {
        "score": final_score,
        "passed": passed,
        "status": "PASSED" if passed else "FAILED",
        "flags": issues
    })

    return {
        "reel_url": reel_url,
        "score": final_score,
        "passed": passed,
        "duration": duration,
        "results": results,
        "issues": issues,
        "positives": positives,
        "overlay_rule_applied": True
    }


# ===============================
# BATCH
# ===============================
def run_batch_pipeline(reel_urls):
    return [run_single_pipeline(url) for url in reel_urls]


# backward compatibility
run_pipeline = run_single_pipeline