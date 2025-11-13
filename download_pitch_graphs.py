import os
import csv
from time import sleep
from bs4 import BeautifulSoup
from PIL import Image
import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# -------------------------------------------------
# ★★ SETTINGS – edit only this block ★★
# -------------------------------------------------
CSV_PATH          = "MyFile.csv"   # CSV file to read
OUTPUT_DIR        = "pitch_graph"          # folder where PNGs will be saved
HEADLESS          = True                   # run Firefox without a visible window
CROP_TOP_PIXELS   = 60                     # pixels to cut off the top of the screenshot
CROP_BOTTOM_PIXELS= 15                     # pixels to cut off the bottom

# ----- CSV column numbers (0‑based) -----
FILENAME_COL      = 0   # column that contains the desired output filename (e.g. Anki card UUID)
TEXT_COL          = 1   # column that contains the Japanese phrase to process
# -------------------------------------------------

# -----------------------------------------------------------------
# Setup: install driver and prepare Firefox options
# -----------------------------------------------------------------
geckodriver_autoinstaller.install()

options = FirefoxOptions()
if HEADLESS:
    options.add_argument('-headless')

# -----------------------------------------------------------------
# Helper: download a single pitch‑accent graph
# -----------------------------------------------------------------
def get_pitched_text(text, filename=None, driver=None):
    # ensure output folder exists
    if OUTPUT_DIR not in os.listdir():
        os.mkdir(OUTPUT_DIR)

    # strip HTML tags / non‑breaking spaces
    clean_text = BeautifulSoup(f"<div>{text}</div>", "html.parser").get_text().replace("\xa0", "")

    if filename is None:
        filename = clean_text
    png_path = f"{OUTPUT_DIR}/{filename}.png"
    if os.path.exists(png_path):
        return png_path

    try:
        print(f"Getting graph from OJAD: {clean_text} → {filename}.png")
        driver.get("https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing")

        # ---- input the Japanese text ----
        input_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "PhrasingText"))
        )
        input_el.send_keys(clean_text)

        # ---- submit the form ----
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "phrasing_submit_wrapper"))
        ).find_element(By.TAG_NAME, "input")
        submit_btn.click()

        # ---- wait for the graph container ----
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "phrasing_main"))
        )

        # ---- hide UI elements we don’t need in the screenshot ----
        driver.execute_script("""
            var styleElement = document.createElement('style');
            styleElement.innerText = `
                input { display: none; }
                font { display: none; }
                select { display: none; }
                * { padding: 0; margin: 0; }
                #phrasing_main { width: fit-content; }
                .ds_t { display: none; }
            `;
            document.body.appendChild(styleElement);
        """)

        # ---- take screenshot ----
        driver.find_element(By.ID, "phrasing_main").screenshot(png_path)

        # ---- crop excess whitespace ----
        with Image.open(png_path) as img:
            left   = 0
            upper  = CROP_TOP_PIXELS
            right  = img.width
            lower  = img.height - CROP_BOTTOM_PIXELS
            img.crop((left, upper, right, lower)).save(png_path)

        return png_path

    except Exception as e:
        print("Error:", e)

# -----------------------------------------------------------------
# Main driver: process the whole CSV
# -----------------------------------------------------------------
def process_file(file_path):
    driver = webdriver.Firefox(options=options)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].startswith('#'):
                    continue
                if len(row) <= max(FILENAME_COL, TEXT_COL):
                    print("Skipping row with insufficient columns:", row)
                    continue

                filename = row[FILENAME_COL]   # user‑chosen column for output name
                text     = row[TEXT_COL]       # user‑chosen column for Japanese phrase

                get_pitched_text(text, filename, driver)
    finally:
        driver.quit()

# -----------------------------------------------------------------
# Run
# -----------------------------------------------------------------
process_file(CSV_PATH)
