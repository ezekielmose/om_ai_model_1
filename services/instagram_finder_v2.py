from scraper.google_selenium import google_search
from scraper.extractor import (
    extract_instagram_candidates,
    get_followers,
    extract_profile_text
)

from rapidfuzz import fuzz
import time


# -----------------------------
# FUZZY MATCH SCORE
# -----------------------------
def fuzzy_score(text, keyword):
    if not text or not keyword:
        return 0

    return fuzz.partial_ratio(keyword.lower(), text.lower()) / 100


# -----------------------------
# MAIN FUNCTION (CLOUD SAFE)
# -----------------------------
def find_instagram_profile(hotel, city, country):

    query = f"{hotel} {city} {country} site:instagram.com"

    # =============================
    # 🔥 UPDATED: NO SELENIUM
    # =============================
    results = google_search(query)

    if isinstance(results, dict) and "error" in results:
        return None

    if not results:
        return None

    # convert URLs into candidate format expected by your pipeline
    candidates = extract_instagram_candidates(results)

    ranked_candidates = []

    for c in candidates:
        try:
            username = c.get("username")
            url = c.get("url")

            # =============================
            # ❌ REMOVED: driver.get(url)
            # ❌ REMOVED: time.sleep()
            # ❌ REMOVED: Selenium calls
            # =============================

            # instead we extract profile text directly from URL
            profile_text = extract_profile_text(url)

            text = f"{username or ''} {url or ''} {profile_text}"

            # -----------------------------
            # FUZZY SCORES
            # -----------------------------
            hotel_score = fuzzy_score(text, hotel)
            city_score = fuzzy_score(text, city)
            country_score = fuzzy_score(text, country)

            followers = get_followers(url)

            total_score = (
                hotel_score * 60 +
                city_score * 25 +
                country_score * 15 +
                (followers / 1000 if followers else 0)
            )

            ranked_candidates.append({
                "username": username,
                "url": url,
                "followers": int(followers or 0),
                "hotel_score": round(hotel_score, 2),
                "city_score": round(city_score, 2),
                "country_score": round(country_score, 2),
                "total_score": total_score
            })

        except Exception as e:
            print("Error:", e)
            continue

    # -----------------------------
    # NO RESULTS
    # -----------------------------
    if not ranked_candidates:
        return None

    # -----------------------------
    # SORT BEST MATCH
    # -----------------------------
    ranked_candidates.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )

    best = ranked_candidates[0]

    # -----------------------------
    # STRICT MATCH FILTER
    # -----------------------------
    MIN_HOTEL_SCORE = 0.6
    MIN_TOTAL_SCORE = 30

    if (
        best["hotel_score"] < MIN_HOTEL_SCORE or
        best["total_score"] < MIN_TOTAL_SCORE
    ):
        return None

    best["score"] = 1
    return best
