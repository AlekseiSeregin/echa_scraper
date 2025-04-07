from xml.dom import NOT_FOUND_ERR

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


URL = "https://echa.europa.eu/information-on-chemicals"
COOKIE_BUTTON = "wt-ecl-button.wt-ecl-button--primary.cck-actions-button"
DISCLAIMER_CHECKBOX = "disclaimerIdCheckboxLabel"
SEARCH_FIELD = "autocompleteKeywordInput"
SEARCH_BUTTON = "_disssimplesearchhomepage_WAR_disssearchportlet_searchButton"
NOT_FOUND_BANNER = "alert.alert-info"
DRIVER_PATH = "chromedriver.exe"
CAS_NUMBER = "2785-89-99"
TIMEOUT = 3

def find_elem(timeout, search_elem, by_what, driver):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_what, search_elem)))

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get(URL)

# cookie_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, COOKIE_BUTTON)))
cookie_button = find_elem(TIMEOUT, COOKIE_BUTTON, By.CLASS_NAME, driver)
cookie_button.click()

# checkbox = driver.find_element(By.CLASS_NAME, DISCLAIMER_CHECKBOX)
checkbox = find_elem(TIMEOUT, DISCLAIMER_CHECKBOX, By.CLASS_NAME, driver)
if not checkbox.is_selected():
    checkbox.click()

# input_element = driver.find_element(By.ID, SEARCH_FIELD)
input_element = find_elem(TIMEOUT, SEARCH_FIELD, By.ID, driver)
input_element.clear()
input_element.send_keys(CAS_NUMBER)

# search_button = driver.find_element(By.ID, SEARCH_BUTTON)
search_button = find_elem(TIMEOUT, SEARCH_BUTTON, By.ID, driver)
search_button.click()

# not_found_banner = driver.find_elements(By.CLASS_NAME, "_disssimplesearch_WAR_disssearchportlet_rmlSearchResultVOsSearchContainerEmptyResultsMessage")
# not_found_banner = driver.find_elements(By.CLASS_NAME, NOT_FOUND_BANNER)
not_found_banner = find_elem(TIMEOUT, NOT_FOUND_BANNER, By.CLASS_NAME, driver)

if not_found_banner:
    print("Not Found")
else:
    # Locate all result rows except the lfr-template
    time.sleep(2)
    rows = driver.find_elements(
        By.XPATH,
        "//tbody[contains(@class, 'table-data')]/tr[not(contains(@class, 'lfr-template'))]"
    )

    print(f"Rows found: {len(rows)}")

    if not rows:
        print("No data rows found.")
    else:
        # In your table, CAS no. is the 3rd <td> (index 2)
        cas_td = rows[0].find_elements(By.TAG_NAME, "td")[2]  # 0-based index
        cas_text = cas_td.text.strip()

        print(f"Found CAS: {cas_text}")

        if cas_text == CAS_NUMBER:
            print("CAS number matches!")
        else:
            print("CAS number does not match.")

time.sleep(3)
driver.quit()
