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
driver.get("https://epc.brp.com/#")
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

csv_file = f"csv/16_Lynx_2_input_{timestamp}.csv"

print("Started!")
save_to_csv(["Brand", "Type", "Year", "Model", "Diagram Name", "Diagram URL"], csv_file)

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
        time.sleep(1)
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
            if(int(year)>2007):
                continue
            # if int(year) > 2001:
            #     continue
            # Scroll the element into view and click
            safe_click(driver, year_elements[i])
            time.sleep(1)
            print(f"Clicked on the year: {years[i]}")
            

            # Wait for the <ul> list to load for the selected year
            ul_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ari-hierarchyLvl"))
            )

            # Locate all <li> elements within the <ul>
            li_elements = ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")
            type_cnt = len(li_elements)
            for type_i in range(type_cnt):
                # Wait for the <ul> list to load for the selected year
                ul_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ari-hierarchyLvl"))
                )                
                type_elements = ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")
                type_li = type_elements[type_i]
                type = type_li.text.strip()
                safe_click(driver, type_li)
                time.sleep(1)
                
                if int(year) <= 2007:
                    try:
                        print('show more finding...')
                        show_more_button = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "ari-item-show-more"))
                        )
                        print('show more found...')
                        if show_more_button.is_displayed():  
                            safe_click(driver, show_more_button)                                  
                            time.sleep(1)
                        else:
                            print("Show More button exists but is not visible.")
                    except Exception as e:
                        print("Show More button did not appear within the timeout.")
                    items_container = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.ari-product-line"))
                    )

                    # Find all 'item' divs inside the container
                    items = items_container.find_elements(By.CLASS_NAME, "item")

                

                    # Extract data from each item
                    for item in items:                    
                        title = item.get_attribute("title")
                        slug = item.get_attribute("slug")
                        if title and slug:
                            save_to_csv([brand, type, year, model, title, slug], csv_file)

                    back_items = WebDriverWait(driver, 20).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "ari-breadCrumbItem"))
                    )

                    safe_click(driver, back_items[1])
                    time.sleep(1)    
                    continue     
                # Wait for the second <ul> element to load
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")) >= 2
                )

                model_ul_elements = driver.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")
                model_ul_element = model_ul_elements[1]
                model_li_elements = model_ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")
                model_li_cnt = len(model_li_elements)
                for j in range(model_li_cnt):
                    print(j)

                    # Wait for the second <ul> element to load
                    WebDriverWait(driver, 20).until(
                        lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")) >= 2
                    )
                    print("passed!")
                    model_ul_elements = driver.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")

                    model_ul_element = model_ul_elements[1]
                    model_li_elements = model_ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")  
                    model_li = model_li_elements[j]
                    model = model_li.text.strip()
                    safe_click(driver, model_li)
                    time.sleep(1)
                    if int(year) <= 2023:
                        try:
                            print('show more finding...')
                            show_more_button = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "ari-item-show-more"))
                            )
                            print('show more found...')
                            if show_more_button.is_displayed():  
                                safe_click(driver, show_more_button)                                  
                                time.sleep(1)
                            else:
                                print("Show More button exists but is not visible.")
                        except Exception as e:
                            print("Show More button did not appear within the timeout.")
                        items_container = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ari-product-line"))
                        )

                        # Find all 'item' divs inside the container
                        items = items_container.find_elements(By.CLASS_NAME, "item")

                    

                        # Extract data from each item
                        for item in items:                    
                            title = item.get_attribute("title")
                            slug = item.get_attribute("slug")
                            if title and slug:
                                save_to_csv([brand, type, year, model, title, slug], csv_file)

                        back_items = WebDriverWait(driver, 20).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "ari-breadCrumbItem"))
                        )

                        safe_click(driver, back_items[2])
                        time.sleep(1)         
                    else:
                        # Wait for the second <ul> element to load
                        WebDriverWait(driver, 20).until(
                            lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")) >= 3
                        )

                        sub_model_ul_elements = driver.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")
                        sub_model_ul_element = sub_model_ul_elements[2]
                        sub_model_li_elements = sub_model_ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")
                        sub_model_li_cnt = len(sub_model_li_elements)
                        for k in range(sub_model_li_cnt):   
                            print(k)
                            WebDriverWait(driver, 20).until(
                                lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")) >= 3
                            )
                            sub_model_ul_elements = driver.find_elements(By.CSS_SELECTOR, "ul.ari-hierarchyLvl")
                            sub_model_ul_element = sub_model_ul_elements[2]
                            sub_model_li_elements = sub_model_ul_element.find_elements(By.CLASS_NAME, "ari-hlvlItem")
                            safe_click(driver, sub_model_li_elements[k])

                            print('passed 2!')

                            time.sleep(1)

                            try:
                                print('show more finding...')
                                show_more_button = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "ari-item-show-more"))
                                )
                                print('show more found...')
                                if show_more_button.is_displayed():  
                                    safe_click(driver, show_more_button)                                  
                                    time.sleep(1)
                                else:
                                    print("Show More button exists but is not visible.")
                            except Exception as e:
                                print("Show More button did not appear within the timeout.")
                            items_container = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ari-product-line"))
                            )

                            # Find all 'item' divs inside the container
                            items = items_container.find_elements(By.CLASS_NAME, "item")

                        

                            # Extract data from each item
                            for item in items:                    
                                title = item.get_attribute("title")
                                slug = item.get_attribute("slug")
                                if title and slug:
                                    save_to_csv([brand, type, year, model, title, slug], csv_file)

                            back_items = WebDriverWait(driver, 20).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, "ari-breadCrumbItem"))
                            )

                            safe_click(driver, back_items[3])
                            time.sleep(1)

                time.sleep(1)  # Optional: Delay to avoid DOM issues

            # Click the breadcrumb element to go back to the Lynx brand page
            breadcrumb = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.ari-breadCrumbItem[aria='ari-backToBrandsPage']"))
            )
            safe_click(driver, breadcrumb)
            time.sleep(1)
            print("Clicked on breadcrumb to navigate back to Lynx.")

        # Break out of the loop after processing all years
        break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
