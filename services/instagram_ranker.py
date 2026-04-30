import re
from difflib import SequenceMatcher
from services.hotel_brand_db import detect_brand, get_brand_keywords


# ===============================
# SIMILARITY SCORE
# ===============================
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# ===============================
# OFFICIAL PROFILE BOOST
# ===============================
def is_official(username, brand_keywords):
    username = username.lower()

    return any(k in username for k in brand_keywords)


def is_verified_like(text):
    """
    Heuristics for 'real official page'
    """

    text = text.lower()

    signals = [
        "official",
        "hotel",
        "resort",
        "luxury",
        "worldwide",
    ]

    return any(s in text for s in signals)


# ===============================
# RANKING FUNCTION
# ===============================
def rank_candidates(candidates, hotel_name, city):

    brand = detect_brand(hotel_name)
    brand_keywords = get_brand_keywords(brand) if brand else []

    ranked = []

    for c in candidates:

        username = c.get("username", "")
        url = c.get("url", "")
        text = c.get("text", "")

        score = 0

        # 1. name similarity
        score += similarity(username, hotel_name) * 3

        # 2. city boost
        if city.lower() in text.lower():
            score += 1.5

        # 3. brand boost
        if brand and is_official(username, brand_keywords):
            score += 3

        # 4. verified-like content
        if is_verified_like(text):
            score += 1

        ranked.append({
            **c,
            "score": score
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked
