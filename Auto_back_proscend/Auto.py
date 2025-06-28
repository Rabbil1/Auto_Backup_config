from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import shutil
import time
import re
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("DEVICE_USERNAME")
PASSWORD = os.getenv("DEVICE_PASSWORD")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", r"C:\Users\YourUser\Downloads")
MAIN_BACKUP_DIR = os.getenv("MAIN_BACKUP_DIR", r"C:\Backup")
BRANCH_FILE = os.getenv("BRANCH_FILE", r"C:\Path\to\YourBranchList.txt")

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip().rstrip(".")

chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(service=Service(), options=chrome_options)
wait = WebDriverWait(driver, 20)

branches = []
with open(BRANCH_FILE, "r", encoding="utf-8") as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split(",") if p.strip()]
        if len(parts) >= 3:
            bank, branch, ip = parts[0], parts[1], parts[2]
            branches.append((bank, branch, ip))

for bank_name, branch_name, ip in branches:
    safe_bank = sanitize_filename(bank_name)
    safe_branch = sanitize_filename(branch_name)
    BACKUP_DIR = os.path.join(MAIN_BACKUP_DIR, safe_bank)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    url = ip.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n=== Processing {safe_bank} > {safe_branch} ({url}) ===")

    try:
        driver.get(url)

        try:
            adv_btn = wait.until(EC.element_to_be_clickable((By.ID, "details-button")))
            adv_btn.click()
            proceed_link = wait.until(EC.element_to_be_clickable((By.ID, "proceed-link")))
            proceed_link.click()
            print("✔ Bypassed SSL warning")
        except:
            print("✔ No SSL warning")

        time.sleep(2)

        try:
            driver.execute_script("document.getElementById('menu_management').classList.add('in');")
            driver.execute_script("document.getElementById('menu_management').style.height = 'auto';")
        except:
            pass

        try:
            config_link = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(@href, '#configuration') and contains(text(), 'Configuration')]"
            )))
            config_link.click()
            print("✔ Configuration menu clicked")
        except Exception as e:
            print(f"✘ Failed to click Configuration menu: {e}")

        try:
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "user")))
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "pass")))
            username_field.clear()
            username_field.send_keys(USERNAME)
            password_field.clear()
            password_field.send_keys(PASSWORD)
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]")))
            login_button.click()
            print("✔ Logged in")
        except Exception as e:
            print(f"✘ Login failed: {e}")
            continue

        time.sleep(3)
        try:
            driver.find_element(By.TAG_NAME, "body").click()
        except:
            pass

        try:
            backup_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'backup the running configurations')]"
            )))
            backup_button.click()
            print("✔ Backup initiated")
        except Exception as e:
            print(f"✘ Backup button not found: {e}")
            continue

        time.sleep(6)
        tgz_files = sorted(
            [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith(".tgz")],
            key=lambda x: os.path.getctime(os.path.join(DOWNLOAD_DIR, x)),
            reverse=True
        )

        if tgz_files:
            latest_file = tgz_files[0]
            src_path = os.path.join(DOWNLOAD_DIR, latest_file)
            dst_path = os.path.join(BACKUP_DIR, f"{safe_branch}.tgz")
            try:
                shutil.move(src_path, dst_path)
                print(f"✔ File saved: {dst_path}")
            except Exception as move_err:
                print(f"✘ Failed to move backup file: {move_err}")
        else:
            print(f"✘ No .tgz file downloaded for {safe_branch}")

    except Exception as e:
        print(f"✘ Unexpected error for {safe_branch}: {e}")
        try:
            screenshot_path = os.path.join(BACKUP_DIR, f"error_{safe_branch}.png")
            driver.save_screenshot(screenshot_path)
            print(f"🖼 Screenshot saved at {screenshot_path}")
        except:
            print("✘ Screenshot capture failed")

driver.quit()
