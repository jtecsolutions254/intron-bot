from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
from gtts import gTTS
import pygame
import os
import time
import sys

def run_bot(target_lang='sw'):
    LOGIN_URL = 'https://speech.intron.health/login'
    DASHBOARD_URL = 'https://speech.intron.health/users/list_projects'

    options = Options()
    options.add_argument("--headless")  # ✅ Headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 1
    })

    # Handle PyInstaller frozen state
    if getattr(sys, 'frozen', False):
        chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
    else:
        chromedriver_path = "chromedriver.exe"

    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    wait = WebDriverWait(driver, 60)

    try:
        # 1️⃣ Login
        driver.get(LOGIN_URL)
        print("🌐 Please log in manually (you have 3 minutes)...")
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Logout')]")))
        print("✅ Logged in")

        # 2️⃣ Dashboard
        driver.get(DASHBOARD_URL)
        print("🧭 Navigated to dashboard")

        # 3️⃣ Click Translate
        translate_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Translate")))
        translate_link.click()
        print("✍️ Clicked 'Translate' link")

        # 4️⃣ Click Start Translating
        start_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Start Translating")))
        start_btn.click()
        print("🚀 Started translating")

        translator = Translator()
        last = ""

        # 5️⃣ Loop
        while True:
            eng = wait.until(EC.presence_of_element_located((By.ID, "textBox"))).text.strip()
            if not eng or eng == last:
                time.sleep(2)
                continue

            last = eng
            print("🔹 English:", eng)

            # Translate
            translated = translator.translate(eng, dest=target_lang)
            sw = translated.text.strip()
            print(f"🔁 {target_lang}:", sw)

            textarea = wait.until(EC.presence_of_element_located((By.ID, "predicted")))
            textarea.clear()
            textarea.send_keys(sw)

            driver.find_element(By.ID, "recordBtn").click()
            print("🎙 Recording...")

            # TTS
            tts = gTTS(text=sw, lang=target_lang)
            tts.save("speech.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
            os.remove("speech.mp3")

            wait.until(EC.element_to_be_clickable((By.ID, "stopBtn"))).click()
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.ID, "submitBtn"))).click()
            print("✅ Submitted\n")
            time.sleep(2)

    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        print("🧹 Session ended. Browser is still open.")
