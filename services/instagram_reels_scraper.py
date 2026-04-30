from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


# ===============================
# PERSISTENT PROFILE CONFIG
# ===============================
CHROME_PROFILE_PATH = os.path.join(os.getcwd(), "chrome_instagram_profile")


def create_driver():
    """
    Creates a Chrome driver with persistent login session.
    This prevents repeated Instagram login.
    """
    options = webdriver.ChromeOptions()

    # 🔥 KEY FIX: persistent session
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")

    # stability improvements
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    return webdriver.Chrome(options=options)


# ===============================
# MAIN FUNCTION
# ===============================
def get_reels_from_profile(username, max_scrolls=30):

    url = f"https://www.instagram.com/{username}/reels/"
    driver = None

    try:
        driver = create_driver()

        # =========================
        # OPEN REELS PAGE DIRECTLY
        # =========================
        driver.get(url)

        # 🔥 SESSION CHECK (only if expired)
        if "login" in driver.current_url:
            print("⚠️ Session expired. Please login once in the opened browser.")
            input("After login, press ENTER to continue...")

        # =========================
        # WAIT FOR PAGE LOAD
        # =========================
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        time.sleep(5)

        reels = set()
        last_count = 0
        stable_rounds = 0

        # =========================
        # SCROLL LOOP
        # =========================
        for i in range(max_scrolls):

            print(f"Scrolling {i+1}/{max_scrolls}")

            # scan page multiple times
            for _ in range(2):
                links = driver.find_elements(By.TAG_NAME, "a")

                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and "/reel/" in href:
                            reels.add(href.split("?")[0])
                    except:
                        continue

                time.sleep(1)

            # scroll
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(3)

            # =========================
            # STOPPING LOGIC
            # =========================
            if len(reels) == last_count:
                stable_rounds += 1
            else:
                stable_rounds = 0
                last_count = len(reels)

            if stable_rounds >= 8:
                print("🛑 No new reels detected — stopping")
                break

        # =========================
        # FINAL SWEEP
        # =========================
        print("🔄 Final sweep...")

        for _ in range(3):
            links = driver.find_elements(By.TAG_NAME, "a")

            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and "/reel/" in href:
                        reels.add(href.split("?")[0])
                except:
                    continue

            time.sleep(1)

        # =========================
        # RESULT
        # =========================
        if not reels:
            return {
                "success": False,
                "reels": [],
                "error": f"No reels found for profile '{username}'"
            }

        return {
            "success": True,
            "reels": [{"url": r} for r in reels]
        }

    except Exception as e:
        return {
            "success": False,
            "reels": [],
            "error": str(e)
        }

    finally:
        if driver:
            driver.quit()
