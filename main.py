from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://echa.europa.eu/information-on-chemicals")

cookie_button = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "wt-ecl-button.wt-ecl-button--primary.cck-actions-button"))
)
cookie_button.click()

checkbox = driver.find_element(By.CLASS_NAME, "disclaimerIdCheckboxLabel")
if not checkbox.is_selected():
    checkbox.click()

input_element = driver.find_element(By.ID, "autocompleteKeywordInput")
input_element.clear()
input_element.send_keys("2785-89-9")

search_button = driver.find_element(By.ID, "_disssimplesearchhomepage_WAR_disssearchportlet_searchButton")
search_button.click()

elements = driver.find_elements(By.ID, "_disssimplesearch_WAR_disssearchportlet_rmlSearchResultVOsSearchContainerEmptyResultsMessage")
time.sleep(3)
if not elements:
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

        if cas_text == "2785-89-9":
            print("CAS number matches!")
        else:
            print("CAS number does not match.")

time.sleep(3)
driver.quit()
