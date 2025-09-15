import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import pickle
import os
import datetime
import datetime as dt

from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException

URL = "https://cloud.timeedit.net/kea/web/stud/ri14Y102Q8ZZ65Q36068X0Q45Q990x06gZ6gY0yQ4Y7g969.html"

def todaysDate():
    return datetime.today().strftime('%Y%m%d')


def login(driver):
    username = os.getenv("LOGIN_EMAIL")
    password = os.getenv("LOGIN_PASSWORD")
    if not username or not password:
        raise Exception("LOGIN_EMAIL and LOGIN_PASSWORD environment variables must be set")

    print("🔐 Navigating to ek.skema.com...")
    driver.get("https://cloud.timeedit.net/kea/web/stud/ri14Y102Q8ZZ65Q36068X0Q45Q990x06gZ6gY0yQ4Y7g969.html")

    # Wait for redirect to connect.jobteaser.com
    WebDriverWait(driver, 20).until(
        lambda d: URL in d.current_url
    )
    print("🔄 Landed on connect.skema.com")

    # Click KEA login link (a-tag containing 'KEA' and ('konto' or 'account'))
    for attempt in range(5):
        try:
            print(f"🎓 Looking for EK login link... (attempt {attempt + 1})")
            login_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='loginAuth']"))
            )
            login_link.click()
            print("✅ Clicked EK login link!")

            print("trykker på sign in with kea_sso")
            login_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='ant-btn css-8qnwxq ant-btn-default ant-btn-color-default ant-btn-variant-outlined ant-btn-block auth-config-button']"))
            )
            login_link.click()
            print("har trykket på sign in with kea_sso")
            break
        except Exception as e:
            print(f"❌ EK login link not ready (attempt {attempt + 1}): {e}")
            time.sleep(2)
    else:
        raise Exception("Could not find or click EK login link.")


    # Wait for Microsoft login page to load
    WebDriverWait(driver, 20).until(
        lambda d: "login.microsoftonline.com" in d.current_url
    )
    print("➡️ On Microsoft login page")

    print("del 1")
    email_input = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.NAME, "loginfmt"))
)
    print("del 2")
    email_input.clear()
    email_input.send_keys(username)
    print("del 3")

    # Vent på knappen og klik
    next_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "idSIButton9"))
)
    print("del 4")
    next_btn.click()
    print("➡️ Submitted email")


# Enter password
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "passwd"))
    )
    password_input = driver.find_element(By.NAME, "passwd")
    password_input.clear()
    password_input.send_keys(password)

    # Retry clicking sign-in button in case of stale element
    for attempt in range(3):
        try:
            sign_in_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            time.sleep(1)  # short delay before clicking
            sign_in_btn.click()
            print("➡️ Submitted password")
            break
        except StaleElementReferenceException:
            print(f"⚠️ Stale element, retrying click attempt {attempt + 1}")
            time.sleep(1)
    else:
        raise Exception("Failed to click the sign-in button after retries")

    # Handle "Stay signed in?" prompt if it appears
    try:
        stay_signed_in_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "idBtn_Back"))
        )
        stay_signed_in_btn.click()
        print("➡️ Dismissed 'Stay signed in?' prompt")
    except Exception:
        print("➡️ No 'Stay signed in?' prompt appeared")

    # Wait for redirect back to kea.jobteaser.com or jobteaser domain after login
    WebDriverWait(driver, 60).until(
        lambda d: any(domain in d.current_url for domain in [URL])
    )
    print("🎉 Successfully logged in and redirected!")




def scrapeTo():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless")  # Uncomment for headless

    class PatchedChrome(uc.Chrome):
        def __del__(self):
            pass  # suppress undetected_chromedriver cleanup bug

    driver = PatchedChrome(options=options)
    print("Browser launched")

    driver.get(URL)
    login(driver)  # ✅ du har allerede en login-metode

    driver.get(URL)
    print("Target URL requested")

    # ⏳ Vent til skemaet er loaded
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.weekDiv"))
        )
    except Exception as e:
        print("Timeout waiting for schedule:", e)
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    print("Soup ready")

    # 📅 Find dagens dato i formatet YYYYMMDD
    today = dt.date.today().strftime("%Y%m%d")

    print("Looking for date:", today)

    # Find den rigtige dag i skemaet
    week_div = soup.find("div", {"class": "weekDiv", "data-dates": today})
    if not week_div:
        print(f"No schedule found for {today}")
        driver.quit()
        return []

    # Hent alle booking-divs for dagen
    data = []
    for booking in week_div.find_all("div", class_="bookingDiv"):
        title = booking.get("title")
        if not title:
            continue

        # Eksempel parsing (tid, fag, lærer, lokale)
        parts = title.split(", ")
        time = parts[0].split(" ", 3)[0] + " " + parts[0].split(" ", 3)[1] + " " + parts[0].split(" ", 3)[2]
        subject = parts[1] if len(parts) > 1 else ""
        teacher = parts[2] if len(parts) > 2 else ""
        room = parts[3].split(" Id ")[0] if len(parts) > 3 else ""

        data.append({
            "time": time,
            "subject": subject,
            "teacher": teacher,
            "room": room
        })

    driver.quit()
    print("Browser closed")
    print(data)
    return data


