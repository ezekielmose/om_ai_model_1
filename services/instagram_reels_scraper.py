import requests
from bs4 import BeautifulSoup


# ===============================
# MAIN FUNCTION (NO SELENIUM)
# ===============================
def get_reels_from_profile(username, max_scrolls=0):
    """
    Cloud-safe Instagram reel extractor (no browser automation)
    """

    try:
        url = f"https://www.instagram.com/{username}/reels/"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {
                "success": False,
                "reels": [],
                "error": f"HTTP {response.status_code}"
            }

        soup = BeautifulSoup(response.text, "html.parser")

        reels = set()

        # extract reel links from HTML
        for a in soup.find_all("a"):
            href = a.get("href")

            if href and "/reel/" in href:
                if href.startswith("/"):
                    href = "https://www.instagram.com" + href

                reels.add(href.split("?")[0])

        # fallback if Instagram blocks content
        if not reels:
            return {
                "success": False,
                "reels": [],
                "error": f"No reels found (Instagram may be blocking scraping for {username})"
            }

        return {
            "success": True,
            "reels": [{"url": r} for r in list(reels)]
        }

    except Exception as e:
        return {
            "success": False,
            "reels": [],
            "error": str(e)
        }
