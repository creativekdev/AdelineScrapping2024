import requests
from lxml import html
import csv
from datetime import datetime

def fetch_html(url):
    """
    Fetch HTML content from a URL.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch URL ({response.status_code}): {url}")

def extract_by_xpath(doc, xpath):
    """
    Extract the brand from the HTML document using the provided XPath.
    """
    elements = doc.xpath(xpath)
    if elements:
        return elements[0].text.strip()
    else:
        raise Exception("Brand not found. Check the XPath.")

def save_to_csv(data, file_name):
    """
    Save the data to a CSV file, ensuring all fields are quoted.
    """
    with open(file_name, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(data)  # Write data

def main():
    base_url = "https://partsfinder.onlinemicrofiche.com"
    brand_url = "/blackfootonline/showmodel/11/suzukisc"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_file = f"csv/4_Suzuki_partsfinder_scooter_1_{timestamp}.csv"
    
    print("started!")
    save_to_csv(["Brand", "Type", "Year", "Model", "URL"], csv_file)
    try:
        type_content = fetch_html(base_url + brand_url)
        type_doc = html.fromstring(type_content)
        year_elements = type_doc.xpath('//div[@class="year_container man_Container_3"]//a')
        for year_element in year_elements:
            href_year = year_element.get('href')
            print(href_year)
            try:
                year_content = fetch_html(href_year)             
                year_doc = html.fromstring(year_content)                
                brand = extract_by_xpath(year_doc, '//*[@id="model_HierarchyMake"]/a')
                type = extract_by_xpath(year_doc, '//*[@id="model_HierarchyLine"]/a')
                year = extract_by_xpath(year_doc, '//*[@id="model_HierarchyYear"]/a')
                model_elements = year_doc.xpath('//div[@class="model_container man_Container_1"]//a')

                for model_element in model_elements:
                    url = model_element.get('href')
                    div_text = model_element.xpath('./div/text()')

                    model = div_text[0].strip() if div_text else "No model text found"  # Get the text or a default value
                    save_to_csv([brand, type, year, model, url], csv_file)
            except Exception as e:
                print(f"Skipping year URL due to error: {e}")
    except Exception as e:
        print(f"Skipping type URL due to error: {e}")
    print("ended successfully!")


if __name__ == "__main__":
    main()
