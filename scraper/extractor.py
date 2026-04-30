from bs4 import BeautifulSoup


# ===============================
# EXTRACT INSTAGRAM LINKS
# ===============================
def extract_instagram_candidates(results):
    """
    Converts Google search results into Instagram profile candidates.
    Now works WITHOUT Selenium.
    """

    candidates = []

    if not results:
        return []

    # if results already come as URLs
    if isinstance(results, list):
        for url in results:
            if "instagram.com" in url:
                username = url.rstrip("/").split("/")[-1]

                candidates.append({
                    "username": username,
                    "url": url
                })

    # fallback for dict responses
    elif isinstance(results, dict):
        for url in results.get("results", []):
            if "instagram.com" in url:
                username = url.rstrip("/").split("/")[-1]

                candidates.append({
                    "username": username,
                    "url": url
                })

    return candidates


# ===============================
# PROFILE TEXT EXTRACTION (SAFE)
# ===============================
def extract_profile_text(url):
    """
    Cloud-safe fallback (no Selenium)
    """

    try:
        import requests

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        # Instagram blocks most text, so we return meta fallback
        title = soup.title.string if soup.title else ""

        return title or ""

    except Exception:
        return ""


# ===============================
# FOLLOWER EXTRACTION (SAFE FALLBACK)
# ===============================
def get_followers(url):
    """
    Instagram hides followers in JS → fallback only
    """

    return 0
