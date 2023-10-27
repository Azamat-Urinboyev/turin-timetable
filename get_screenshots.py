from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import pandas as pd
import time
import os

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920x900")
options.binary_location = "chromedriver"



def take_timetable_screenshots(url, file_path, excluded_groups, lan="en"):
    if lan == "en":
        title = "Classes"
    elif lan == "rus":
        title="Классы"


    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.maximize_window()

    classes = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'span[title="{title}"]')))
    # classes = driver.find_element(by=By.CSS_SELECTOR, value='span[title="Classes"]')

    driver.execute_script("arguments[0].click();", classes)
    time.sleep(1)

    ul_element = driver.find_element(By.CLASS_NAME, "dropDownPanel.asc-context-menu")
    groups= ul_element.find_elements(By.TAG_NAME, "li")

    new_groups = dict()
    for group in groups:
        group_name = group.text
        if group_name in excluded_groups:    ##clean some useless groups
            continue
        new_groups[group_name] = group

    for group_name, group in new_groups.items():
        driver.execute_script("arguments[0].click();", group)
        driver.save_screenshot(f"screenshots/{file_path}/{group_name}.png")

    driver.quit()

    
def crop_screenshots(x1, x2, y1, y2, file_path):
    images = os.listdir(f"screenshots/{file_path}")
    
    for image in images:
        full_screenshot = Image.open(f"screenshots/{file_path}/{image}")

        cropped_screenshot = full_screenshot.crop((x1, y1, x2, y2))
        cropped_screenshot.save(f"screenshots/{file_path}/{image}")
        full_screenshot.close()



def run():
    screenshots_path = "./screenshots"
    if not os.path.exists(screenshots_path):
        os.mkdir(path=screenshots_path)
    univer_info = pd.read_csv("./data/univer_info.csv")
    x1 = 450
    y1 = 117
    x2 = 1440
    y2 = 770

    for index, row in univer_info.iterrows():
        url = row.iloc[1]
        lan = row.iloc[2]
        file_path = row.iloc[3]
        excluded_groups = str(row.iloc[4]).split(";")

        full_file_path = f"{screenshots_path}/{file_path}"
        if not os.path.exists(full_file_path):
            os.mkdir(full_file_path)


        take_timetable_screenshots(url=url, file_path=file_path, excluded_groups=excluded_groups, lan=lan)
        crop_screenshots(x1, x2, y1, y2, file_path)



run()