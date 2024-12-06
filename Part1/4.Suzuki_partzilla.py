from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime
import os

def save_to_csv(data, file_name):
    """
    Save the data to a CSV file, ensuring all fields are quoted.
    """
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(data)

def scrape_models(driver, base_url, csv_file):
    try:
        model_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="catalog-table hidden-xs hidden-sm"]//td/a'))
        )

        for model_element in model_elements:
            model_url = base_url + model_element.get_attribute('href')
            model_name = model_element.text
            save_to_csv([driver.brand, driver.type_name, driver.year_name, model_name, model_url], csv_file)
    except Exception as e:
        print(f"Skipping models due to error: {e}")

def scrape_years(driver, href, base_url, csv_file):
    driver.get(href)
    try:
        driver.type_name = driver.find_element(By.XPATH, '/html/body/main/article/div/section/div[1]/div/div/ol/li[3]/a').text
        year_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="catalog-table hidden-xs hidden-sm"]//td/a'))
        )

        for year_element in year_elements:
            href_year = year_element.get_attribute('href')
            driver.year_name = year_element.text

            driver.get(href_year)
            scrape_models(driver, base_url, csv_file)
    except Exception as e:
        print(f"Skipping year URL due to error: {e}")

def scrape_types(driver, base_url, brand_url, csv_file):
    driver.get(base_url + brand_url)

    try:
        type_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="catalog-table hidden-xs hidden-sm"]//td/a'))
        )

        for type_element in type_elements:
            href = type_element.get_attribute('href')
            driver.type_text = type_element.text
            scrape_years(driver, href, base_url, csv_file)
    except Exception as e:
        print(f"Skipping type due to error: {e}")

def main():
    base_url = "https://www.partzilla.com"
    brand_url = "/catalog/suzuki"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_file = f"csv/4_Suzuki_partzilla_1_{timestamp}.csv"

    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # Extend driver with custom attributes
    driver.brand = "Suzuki"
    driver.type_name = ""
    driver.year_name = ""

    try:
        print("Started!")
        save_to_csv(["Brand", "Type", "Year", "Model", "URL"], csv_file)
        scrape_types(driver, base_url, brand_url, csv_file)
        print("Ended successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()