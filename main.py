from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import sys
from utils import *


service = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=service)
driver.get(URL)

language_select = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, LANG_ELEM)))
select = Select(language_select)
select.select_by_value(LANG)

cookie_button = find_elem(TIMEOUT, COOKIE_BUTTON, By.CSS_SELECTOR, driver)
cookie_button.click()

checkbox = find_elem(TIMEOUT, DISCLAIMER_CHECKBOX, By.CLASS_NAME, driver)
if not checkbox.is_selected():
    checkbox.click()

input_element = find_elem(TIMEOUT, SEARCH_FIELD, By.ID, driver)
input_element.clear()
input_element.send_keys(CAS_NUMBER)

search_button = find_elem(TIMEOUT, SEARCH_BUTTON, By.ID, driver)
search_button.click()

try:
    WebDriverWait(driver, TIMEOUT).until(
        EC.any_of(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".table.table-bordered")),
            EC.visibility_of_element_located((By.ID, NOT_FOUND_BANNER))))
    no_results_el = driver.find_element(By.ID,NOT_FOUND_BANNER)

    if no_results_el.is_displayed():
        print("No results found (message is visible). Exiting.")
        sys.exit(1)

except Exception as e:
    print("Error or timeout while checking for search result visibility.")
    print(e)
    sys.exit(1)

print("Results found! Continue.")

first_row_cas = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//table[contains(@class, 'table')]/tbody/tr[1]/td[3]//span[@class='highlight']")))

cas_value = first_row_cas.text.strip()
if cas_value == CAS_NUMBER:
    print(f"Match found: {cas_value}")
else:
    print(f"No match. Found: {cas_value}, Expected: {CAS_NUMBER}")

first_result_link = WebDriverWait(driver, TIMEOUT).until(
    EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        'tbody.table-data > tr:not(.lfr-template) td.first a.substanceNameLink')))
first_result_link.click()

button = WebDriverWait(driver, TIMEOUT).until(
    EC.element_to_be_clickable((By.ID, CL_INVENTORY_BUTTON)))
if button:
    button.click()

window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])
classification_data = {"CAS_NUMBER": CAS_NUMBER, "CLASSIFICATIONS": {}}
extract_classification_data(driver, classification_data)
save_data_to_json(classification_data)
driver.quit()
