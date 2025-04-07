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


COOKIE_BUTTON = "a.wt-ecl-button.wt-ecl-button--primary.cck-actions-button[href='#accept']"
DISCLAIMER_CHECKBOX = "disclaimerIdCheckboxLabel"
SEARCH_FIELD = "autocompleteKeywordInput"
SEARCH_BUTTON = "_disssimplesearchhomepage_WAR_disssearchportlet_searchButton"
URL = "https://echa.europa.eu/information-on-chemicals"
NOT_FOUND_BANNER = "alert alert-info "
DRIVER_PATH = "chromedriver.exe"
# CAS_NUMBER = "2785-89-9"
CAS_NUMBER = "7440-48-4"
LANG_ELEM = "languageId"
LANG = "en_GB"

TIMEOUT = 5


def find_elem(timeout, search_elem, by_what, driver):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by_what, search_elem)))


# Function to extract classification data
def extract_classification_data(driver):
    classification_data = []

    try:
        # Wait for the table containing the classification data to be present
        classification_table = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "CLPtable"))
        )

        # Wait until the table body is populated (ensure dynamic content is loaded)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 "//table[contains(@class, 'CLPtable') and contains(@class, 'taglib-search-iterator')]//tr[contains(@class, 'results-row')]"))
        )

        # Check if the table exists
        if classification_table:
            rows = classification_table.find_elements(By.XPATH, ".//tbody//tr[contains(@class, 'results-row')]")

            if not rows:
                print("No classification rows found.")
            else:
                # Loop through each row and extract relevant data
                for row in rows:
                    # Extracting classification details
                    hazard_class = row.find_element(By.XPATH, ".//td[1]").text.strip()
                    hazard_statement = row.find_element(By.XPATH, ".//td[2]").text.strip()
                    supplementary_hazard_statement = row.find_element(By.XPATH, ".//td[3]").text.strip() if len(
                        row.find_elements(By.XPATH, ".//td[3]")) > 0 else ""
                    signal_word = row.find_element(By.XPATH,
                                                   ".//td[5]").text.strip()  # Adjusting for signal word column
                    pictogram = row.find_element(By.XPATH, ".//td[6]//img").get_attribute("alt") if len(
                        row.find_elements(By.XPATH, ".//td[6]//img")) > 0 else ""  # Pictogram column

                    # Append extracted data to the classification_data list
                    classification_data.append({
                        "Hazard Class": hazard_class,
                        "Hazard Statement": hazard_statement,
                        "Supplementary Hazard Statement": supplementary_hazard_statement,
                        "Signal Word": signal_word,
                        "Pictogram": pictogram
                    })

            # Return classification data
            return classification_data

    except Exception as e:
        print(f"An error occurred: {e}")

    return classification_data


# Function to save data in JSON format
def save_data_to_json(data, filename="classification_data.json"):
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

# Extract the classification data
classification_data = extract_classification_data(driver)

# If classification data exists, save it to a JSON file
if classification_data:
    save_data_to_json(classification_data)
else:
    print("No classification data to save.")

time.sleep(3)
driver.quit()
