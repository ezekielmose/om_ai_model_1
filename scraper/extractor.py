from bs4 import BeautifulSoup
import requests
import re


# ===============================
# CLEAN GOOGLE + RAW RESULTS
# ===============================
def clean_urls(results):
    """
    Removes Google junk and keeps only valid Instagram URLs
    """

    clean = []

    if not results:
        return clean

    # handle list
    if isinstance(results, list):
        for url in results:
            if not url:
                continue

            # remove Google search URLs
            if "search?q=" in url:
                continue

            # keep only Instagram
            if "instagram.com" in url:
                clean.append(url)

    # handle dict
    elif isinstance(results, dict):
        for url in results.get("results", []):
            if url and "instagram.com" in url and "search?q=" not in url:
                clean.append(url)

    return clean


# ===============================
# EXTRACT INSTAGRAM CANDIDATES
# ===============================
def extract_instagram_candidates(results):
    """
    Converts cleaned URLs into structured candidates
    """

    urls = clean_urls(results)
    candidates = []

    for url in urls:
        try:
            # remove query params
            url = url.split("?")[0].strip("/")

            parts = url.split("/")

            # basic validation
            if len(parts) < 4:
                continue

            username = parts[-1]

            # skip invalid usernames
            if not username or username in ["reel", "p", "explore"]:
                continue

            candidates.append({
                "username": username,
                "url": url
            })

        except Exception:
            continue

    return candidates


# ===============================
# PROFILE TEXT EXTRACTION (IMPROVED)
# ===============================
def extract_profile_text(url):
    """
    Extracts useful signals from Instagram page
    (bio, title, meta description fallback)
    """

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return ""

        soup = BeautifulSoup(r.text, "html.parser")

        # title (username + page info)
        title = soup.title.string if soup.title else ""

        # meta description (VERY IMPORTANT SIGNAL)
        meta = soup.find("meta", property="og:description")
        description = meta["content"] if meta and meta.get("content") else ""

        # fallback text extraction
        page_text = soup.get_text(" ", strip=True)

        # combine signals
        return f"{title} {description} {page_text[:300]}"

    except Exception:
        return ""


# ===============================
# FOLLOWER EXTRACTION (BEST EFFORT)
# ===============================
def get_followers(url):
    """
    Instagram hides followers → fallback approximation
    """

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return 0

        # try to find follower patterns in HTML
        match = re.search(r'([0-9,.]+)\s*(followers|follower)', r.text, re.IGNORECASE)

        if match:
            value = match.group(1).replace(",", "")
            try:
                return int(float(value))
            except:
                return 0

        return 0

    except Exception:
        return 0
