import time
from utils.driver import get_driver


def google_search(query: str):
    driver = get_driver(headless=False)

    url = f"https://www.google.com/search?q={query}"
    driver.get(url)

    # 🔥 IMPORTANT: mimic human behavior
    time.sleep(5)

    return driver
