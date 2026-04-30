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
# FALLBACK INSTAGRAM HANDLES
# -----------------------------
def generate_fallback_handles(hotel, city):
    base = hotel.lower().replace(" ", "").replace("-", "")

    return [
        f"https://www.instagram.com/{base}/",
        f"https://www.instagram.com/{base}hotel/",
        f"https://www.instagram.com/{city.lower().replace(' ', '')}{base}/",
    ]


# -----------------------------
# MAIN FUNCTION (CLOUD SAFE)
# -----------------------------
def find_instagram_profile(hotel, city, country):

    query = f"{hotel} {city} {country} site:instagram.com"

    results = google_search(query)

    # =============================
    # HANDLE GOOGLE FAILURE
    # =============================
    if not results:
        fallback_urls = generate_fallback_handles(hotel, city)

        candidates = [
            {"username": url.split("/")[-2], "url": url}
            for url in fallback_urls
        ]
    else:
        candidates = extract_instagram_candidates(results)

    ranked_candidates = []

    for c in candidates:
        try:
            username = c.get("username")
            url = c.get("url")

            # =============================
            # PROFILE TEXT EXTRACTION
            # =============================
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
    # NO RESULTS HANDLING
    # -----------------------------
    if not ranked_candidates:
        return None

    # -----------------------------
    # SORT BEST MATCH
    # -----------------------------
    ranked_candidates.sort(key=lambda x: x["total_score"], reverse=True)

    best = ranked_candidates[0]

    # -----------------------------
    # RELAXED THRESHOLD (IMPORTANT FIX)
    # -----------------------------
    MIN_HOTEL_SCORE = 0.4
    MIN_TOTAL_SCORE = 10

    if (
        best["hotel_score"] < MIN_HOTEL_SCORE and
        best["total_score"] < MIN_TOTAL_SCORE
    ):
        return None

    # -----------------------------
    # FINAL OUTPUT
    # -----------------------------
    best["score"] = 1
    return best
