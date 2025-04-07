from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import sys
import time


COOKIE_BUTTON = "a.wt-ecl-button.wt-ecl-button--primary.cck-actions-button[href='#accept']"
DISCLAIMER_CHECKBOX = "disclaimerIdCheckboxLabel"
SEARCH_FIELD = "autocompleteKeywordInput"
SEARCH_BUTTON = "_disssimplesearchhomepage_WAR_disssearchportlet_searchButton"
NOT_FOUND_BANNER = "alert alert-info "
DRIVER_PATH = "chromedriver.exe"
CAS_NUMBER = "2785-89-9"
LANG_ELEM = "languageId"
LANG = "en_GB"

TIMEOUT = 5


def find_elem(timeout, search_elem, by_what, driver):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_what, search_elem)))


URL = "https://echa.europa.eu/information-on-chemicals"
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get(URL)

# Wait until the <select> is present
language_select = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.ID, LANG_ELEM)))
# Create a Select object
select = Select(language_select)
# Select by value (recommended)
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
    # Wait until either results table or the no-results message is visible
    WebDriverWait(driver, 10).until(
        EC.any_of(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".table.table-bordered")),
            EC.presence_of_element_located(
                (By.ID, "_disssimplesearch_WAR_disssearchportlet_rmlSearchResultVOsSearchContainerEmptyResultsMessage"))
        )
    )

    # Check the "no results" div
    no_results_el = driver.find_element(By.ID,
                                        "_disssimplesearch_WAR_disssearchportlet_rmlSearchResultVOsSearchContainerEmptyResultsMessage")

    if no_results_el.is_displayed():
        print("❌ No results found (message is visible). Exiting.")
        sys.exit(1)

except Exception as e:
    print("⚠️ Error or timeout while checking for search result visibility.")
    print(e)
    sys.exit(1)

print("✅ Results found! Continue scraping.")

first_row_cas = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//table[contains(@class, 'table')]/tbody/tr[1]/td[3]//span[@class='highlight']"
        ))
    )

# Extract text and compare
cas_value = first_row_cas.text.strip()
if cas_value == CAS_NUMBER:
    print(f"✅ Match found: {cas_value}")
else:
    print(f"❌ No match. Found: {cas_value}, Expected: {CAS_NUMBER}")


# Wait until the table loads and the first substance name link appears
first_result_link = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        'tbody.table-data > tr:not(.lfr-template) td.first a.substanceNameLink'
    ))
)

# Click it
first_result_link.click()

time.sleep(10)
driver.quit()
