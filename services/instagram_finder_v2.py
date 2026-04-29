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
# MAIN FUNCTION
# -----------------------------
def find_instagram_profile(hotel, city, country):
    query = f"{hotel} {city} {country} site:instagram.com"

    driver = google_search(query)
    candidates = extract_instagram_candidates(driver)

    ranked_candidates = []

    for c in candidates:
        try:
            username = c.get("username")
            url = c.get("url")

            driver.get(url)
            time.sleep(4)

            profile_text = extract_profile_text(driver)

            text = f"{username or ''} {url or ''} {profile_text}"

            # -----------------------------
            # FUZZY SCORES
            # -----------------------------
            hotel_score = fuzzy_score(text, hotel)
            city_score = fuzzy_score(text, city)
            country_score = fuzzy_score(text, country)

            followers = get_followers(driver)

            total_score = (
                hotel_score * 60 +     # strongest signal
                city_score * 25 +
                country_score * 15 +
                (followers / 1000)
            )

            ranked_candidates.append({
                "username": username,
                "url": url,
                "followers": int(followers),
                "hotel_score": round(hotel_score, 2),
                "city_score": round(city_score, 2),
                "country_score": round(country_score, 2),
                "total_score": total_score
            })

        except Exception as e:
            print("Error:", e)
            continue

    driver.quit()

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
    # 🔥 STRICT MATCH FILTER
    # -----------------------------
    MIN_HOTEL_SCORE = 0.6
    MIN_TOTAL_SCORE = 30

    if (
        best["hotel_score"] < MIN_HOTEL_SCORE or
        best["total_score"] < MIN_TOTAL_SCORE
    ):
        return None

    # ✅ VALID MATCH
    best["score"] = 1

    return best
