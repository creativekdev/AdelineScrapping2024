from datetime import datetime
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from lxml import html
import csv


def save_to_csv(data, file_name):
    """
    Save the data to a CSV file, ensuring all fields are quoted.
    """
    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(data)  # Write data


def safe_click(driver, element, max_attempts=3):
    """
    Safely clicks on an element, handling intercepted clicks and scroll issues.
    """
    for attempt in range(max_attempts):
        try:
            # Check if the element exists and is interactable
            if element is None:
                raise Exception("Element is None. It might not be found in the DOM.")

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)
            element.click()
            return
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to click on element. Retrying... ({e})")
            time.sleep(2)
    raise Exception(f"Failed to click on element after {max_attempts} attempts.")


# Set up the WebDriver
driver = webdriver.Chrome()  # Ensure you have the correct WebDriver installed
driver.set_window_size(1920, 1080)  # Set a larger window size to avoid layout issues
driver.set_page_load_timeout(30)  # Timeout in seconds

driver.get("https://epc.brp.com/#")
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
base_url = "https://epc.brp.com/#"
input_file = "result_part1//16_Lynx_2_input.csv"

csv_file = f"csv/16_Lynx_2_output_{timestamp}.csv"

print("Started!")
save_to_csv(["Brand", "Type", "Year", "Model", "Diagram Name", "Ref #", "Part description", "Part number", "OEM diagram URL", "Price", "SSPN"], csv_file)

brand = "Lynx"
type = ""
year = ""
model = ""
url = ""

try:
    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row_number, row in enumerate(reader, start=1):
            if row_number <17232:
                continue
            if len(row) < 5:
                print(f"Skipping invalid row {row_number} in input file: {row}")
                continue
            
            brand = row[0]
            type = row[1]
            year = row[2]
            model = row[3]
            diagram_name = row[4]            
            diagram_url = row[5]            
            driver.get(base_url + diagram_url)
            time.sleep(2)
            try:
                # Use explicit wait to wait for the part list to load
                wait = WebDriverWait(driver, 20)  # Timeout set to 20 seconds
                part_list = wait.until(EC.presence_of_element_located((By.ID, "ariPartList")))

                # Find all parts within the part list
                rows = driver.find_elements(By.XPATH, "//tbody/tr[contains(@class, 'ariPartInfo')]")

                # Loop through each part and extract the desired details
                for row in rows:
                    ref = row.find_element(By.XPATH, ".//td[contains(@class, 'ariPLTag')]").text.strip()
                    part_number = row.find_element(By.XPATH, ".//td[contains(@class, 'ariPLSku')]/span").get_attribute("name").strip()
                    description = row.find_element(By.XPATH, ".//td[contains(@class, 'ariPLDesc')]").text.strip()
                    # Assuming price is stored in an 'adjustedprice' attribute, change if price is located elsewhere
                    price = row.find_element(By.XPATH, ".//td[contains(@class, 'ariPLSku')]").get_attribute("adjustedprice").strip()
                    save_to_csv([brand, type, year, model, diagram_name, ref, description, part_number, diagram_url, price, ""], csv_file)

            except Exception as e:
                print(f"Failed to load parts for diagram URL {diagram_url}: {e}")



except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
