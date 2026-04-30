import requests
from bs4 import BeautifulSoup


def google_search(query: str):
    try:
        url = f"https://www.google.com/search?q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = []

        for a in soup.find_all("a"):
            href = a.get("href")
            if href and "instagram.com" in href:
                links.append(href)

        return links[:5]

    except Exception as e:
        return {
            "error": str(e),
            "results": []
        }
