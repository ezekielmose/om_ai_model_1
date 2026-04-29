from selenium import webdriver
import pickle
import os
import time

COOKIE_FILE = "instagram_cookies.pkl"


# =========================
# START BROWSER
# =========================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)


# =========================
# LOAD COOKIES IF EXIST
# =========================
def load_cookies():
    if os.path.exists(COOKIE_FILE):
        driver.get("https://www.instagram.com/")
        time.sleep(3)

        cookies = pickle.load(open(COOKIE_FILE, "rb"))

        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass

        driver.refresh()
        time.sleep(5)
        return True

    return False


# =========================
# LOGIN FLOW
# =========================
if load_cookies():
    print("✅ Logged in using saved cookies")
else:
    driver.get("https://www.instagram.com/accounts/login/")

    print("\n==============================")
    print("👉 LOGIN MANUALLY IN CHROME")
    print("👉 DO NOT CLOSE BROWSER")
    print("==============================\n")

    input("After login is complete, press ENTER here ONLY... ")

    time.sleep(3)

    pickle.dump(driver.get_cookies(), open(COOKIE_FILE, "wb"))

    print("✅ Cookies saved successfully (valid for reuse)")
    print("You can close browser manually now.")