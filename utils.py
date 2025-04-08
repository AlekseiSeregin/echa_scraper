from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import json
from config import *


def save_data_to_json(data, filename="classification_data.json"):
    filename = SAVE_PATH + filename
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {filename}.")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")


def find_elem(timeout, search_elem, by_what, driver):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_what, search_elem)))


def extract_classification_data(driver, classification_data):
    try:
        classification_table = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//span[text()='{HARMONIZED_TABLE_ANCH}']/following::table[contains(@class, 'CLPtable')]")))

    except TimeoutException:
        try:
            classification_table = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    f"//span[normalize-space(text())='{NOTIFIED_TABLE_ANCH}']/following::table[contains(@class, 'CLPtable')]")))

        except TimeoutException:
            print("Neither the primary nor the secondary table was found.")
            return None

    rows = classification_table.find_elements(By.CSS_SELECTOR, "tbody tr.results-row, tbody tr.results-row-alt")

    if not rows:
        print("No classification rows found.")
    else:
        for ind, row in enumerate(rows):
            if "alt" in row.get_attribute("class"):
                break
            cols = row.find_elements(By.TAG_NAME, "td")
            classification_data["CLASSIFICATIONS"][ind] = {
                "Hazard Class": cols[0].text,
                'hazard_code': cols[1].text,
            }
    return classification_data
