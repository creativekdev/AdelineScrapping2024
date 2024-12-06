from datetime import datetime
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
driver.get("https://epc.brp.com/#")
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

csv_file = f"csv/16_Lynx_1_{timestamp}.csv"

print("Started!")
save_to_csv(["Brand", "Type", "Year", "Model", "URL"], csv_file)

brand = "Lynx"
type = ""
year = ""
model = ""
url = ""

try:
    # Wait for the page to load and locate the Lynx brand logo
    lynx_element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.brandLogoBox[name='LNX_EN_US']"))
    )

    # Click the Lynx brand logo
    safe_click(driver, lynx_element)
    print("Clicked on Lynx!")

    # Loop through each year
    while True:
        show_more = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ari-item-show-more"))
        )
        safe_click(driver, show_more)

        # Wait for the years to load
        year_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ari-product-line div.item p"))
        )

        # Extract and print the year values
        years = [year.text for year in year_elements]
        print("Years available:", years)

        for i in range(len(years)):
            # Refresh the year elements list each time, as the DOM may change after clicking
            year_elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ari-product-line div.item p"))
            )
            year = years[i]
            if int(year) > 2001:
                continue
            # Scroll the element into view and click
            safe_click(driver, year_elements[i])
            print(f"Clicked on the year: {years[i]}")
            

            # Wait for the <ul> list to load for the selected year
            ul_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ari-hierarchyLvl[style*='display: block']"))
            )

            # Locate all <li> elements within the <ul>
            li_elements = ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")

            # Iterate through each <li> element, print details, and click
            for li in li_elements:
                arib = li.get_attribute("arib")
                aria = li.get_attribute("aria")
                type = li.text.strip()
                print(f"Clicking on <li>: arib={arib}, aria={aria}, type={type}")
                
                if int(year) <= 2007:
                    save_to_csv([brand, type, year, "", ""], csv_file)
                    continue

                safe_click(driver, li)

                # Wait for the second <ul> element to load
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl[style*='display: block']")) >= 2
                )

                # Get all <ul> elements with the specified style
                model_ul_elements = driver.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl[style*='display: block']")

                # Check if at least two <ul> elements exist
                if len(model_ul_elements) >= 2:
                    # Select the second <ul> element
                    model_ul_element = model_ul_elements[1]
                    print("Selected the second <ul> element.")
                    model_li_elements = model_ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")
                    for li in model_li_elements:
                        arib = li.get_attribute("arib")
                        aria = li.get_attribute("aria")
                        model = li.text.strip()
                        save_to_csv([brand, type, year, model, url], csv_file)
                else:
                    print("Less than two <ul> elements are available. Skipping this type.")
                    continue

                time.sleep(1)  # Optional: Delay to avoid DOM issues

            # Click the breadcrumb element to go back to the Lynx brand page
            breadcrumb = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.ari-breadCrumbItem[aria='ari-backToBrandsPage']"))
            )
            safe_click(driver, breadcrumb)
            print("Clicked on breadcrumb to navigate back to Lynx.")

        # Break out of the loop after processing all years
        break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
