import re
import time
#from selenium.webdriver.common.by import By
from urllib.parse import urlparse


# -----------------------------
# VALID PROFILE CHECK
# -----------------------------
def is_valid_profile(url: str):
    if not url:
        return False

    if "instagram.com" not in url:
        return False

    blocked = [
        "/p/", "/reel/", "/tv/",
        "/explore/", "/accounts/", "/stories/"
    ]

    if any(b in url for b in blocked):
        return False

    path = urlparse(url).path.strip("/")
    if path == "":
        return False

    return True


# -----------------------------
# USERNAME EXTRACTOR
# -----------------------------
def extract_username(url: str):
    try:
        path = urlparse(url).path.strip("/")
        return path.split("/")[0] if path else None
    except:
        return None


# -----------------------------
# GET FOLLOWERS (ROBUST)
# -----------------------------
def get_followers(driver):
    try:
        time.sleep(4)
        page = driver.page_source.lower()

        match = re.search(r'([\d,.]+[km]?)\s+followers', page)

        if not match:
            return 0

        value = match.group(1).replace(",", "").strip().lower()

        if "m" in value:
            return float(value.replace("m", "")) * 1_000_000
        if "k" in value:
            return float(value.replace("k", "")) * 1_000

        return float(value)

    except Exception as e:
        print("Follower extraction error:", e)
        return 0


# -----------------------------
# NEW: EXTRACT PROFILE TEXT
# -----------------------------
def extract_profile_text(driver):
    try:
        time.sleep(3)

        # Use full page source (contains name + bio)
        page = driver.page_source.lower()

        return page

    except Exception as e:
        print("Profile text extraction error:", e)
        return ""


# -----------------------------
# GOOGLE RESULTS → CANDIDATES
# -----------------------------
def extract_instagram_candidates(driver, limit=5):
    links = driver.find_elements(By.CSS_SELECTOR, "#search a")

    results = []

    for a in links:
        href = a.get_attribute("href")

        if not href:
            continue

        if "google.com" in href:
            continue

        if "/url?q=" in href:
            href = href.split("/url?q=")[1].split("&")[0]

        if is_valid_profile(href):
            username = extract_username(href)

            results.append({
                "url": href,
                "username": username
            })

        if len(results) >= limit:
            break

    return results
