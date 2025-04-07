from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import json
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
import time


URL = "https://echa.europa.eu/information-on-chemicals"
COOKIE_BUTTON = "a.wt-ecl-button.wt-ecl-button--primary.cck-actions-button[href='#accept']"
DISCLAIMER_CHECKBOX = "disclaimerIdCheckboxLabel"
SEARCH_FIELD = "autocompleteKeywordInput"
SEARCH_BUTTON = "_disssimplesearchhomepage_WAR_disssearchportlet_searchButton"
NOT_FOUND_BANNER = "alert alert-info "
DRIVER_PATH = "chromedriver.exe"
# CAS_NUMBER = "2785-89-9"
CAS_NUMBER = "7440-48-4"
LANG_ELEM = "languageId"
LANG = "en_GB"
TIMEOUT = 5


def find_elem(timeout, search_elem, by_what, driver):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_what, search_elem)))


def extract_classification_data(driver, classification_data):
    try:
        classification_table = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//span[text()='CLP Classification (Table 3)']/following::table[contains(@class, 'CLPtable')]")))
    except TimeoutException:
        try:
            classification_table = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//span[normalize-space(text())='Notified classification and labelling according to CLP criteria']/following::table[contains(@class, 'CLPtable')]"))
            )

        except TimeoutException:
            print("Neither the primary nor the secondary table was found.")
            return None

    rows = classification_table.find_elements(By.CSS_SELECTOR, "tbody tr.results-row")
    if not rows:
        print("No classification rows found.")
    else:
        for ind, row in enumerate(rows):
            # Check if this is a results-row (first batch)
            if "alt" in row.get_attribute("class"):
                break
            # Extract data from this row
            cols = row.find_elements(By.TAG_NAME, "td")

            classification_data["CLASSIFICATIONS"][ind] = {
                "Hazard Class": cols[0].text,
                'hazard_code': cols[1].text,
            }

            # cells = row.find_elements(By.TAG_NAME, "td")
            # # Only process rows that have at least 2 cells
            # if len(cells) >= 2:
            #     # Check for empty cells and handle accordingly
            #     hazard_class = cells[0].text.strip() if cells[0].text.strip() != '&nbsp;' else None
            #     hazard_code = cells[1].text.strip() if cells[1].text.strip() != '&nbsp;' else None
            #
            #     # Extract further data if available
            #     hazard_statement = cells[2].text.strip() if len(cells) > 2 and cells[
            #         2].text.strip() != '&nbsp;' else None
            #     # classification_data.append({
            #     #     'hazard_class': hazard_class,
            #     #     'hazard_code': hazard_code,
            #     #     'hazard_statement': hazard_statement
            #     # })
            #     classification_data["CLASSIFICATIONS"][ind] = {
            #         "Hazard Class": hazard_class,
            #         "Hazard Statement": hazard_statement,
            #         'hazard_code': hazard_code,
            #     }


            # hazard_class = row.find_elements(By.CSS_SELECTOR, "td.cli-vertical-align-center")[0].text
            # hazard_statement = row.find_elements(By.CSS_SELECTOR, "td.cli-vertical-align-center")[1].text
            #
            # classification_data["CLASSIFICATIONS"][ind] = {
            #     "Hazard Class": hazard_class,
            #     "Hazard Statement": hazard_statement,
            # }

    return classification_data


def save_data_to_json(data, filename="results/classification_data.json"):
    try:
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data successfully saved to {filename}.")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")


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


# Wait until the button is clickable
button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((
        By.ID, "_disssubsinfo_WAR_disssubsinfoportlet_dataset-cnl-button"
    ))
)
if button:
    # Click the button
    button.click()

# Get all open window handles
window_handles = driver.window_handles
# Switch to the second tab (index 1, as it's 0-based indexing)
driver.switch_to.window(window_handles[1])
# Fill out the classification data
classification_data = {"CAS_NUMBER": CAS_NUMBER, "CLASSIFICATIONS": {}}
extract_classification_data(driver, classification_data)

# If classification data exists, save it to a JSON file
if classification_data:
    save_data_to_json(classification_data)
else:
    print("No classification data to save.")

time.sleep(3)
driver.quit()
