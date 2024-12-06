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
    base_url = "https://www.canampartshouse.com/"
    brand_url = "oemparts/c/can_am/parts"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_file = f"csv/10_Can_Am_1_{timestamp}.csv"
    
    print("started!")
    save_to_csv(["Brand", "Type", "Year", "Model", "URL"], csv_file)

    try:
        html_content = fetch_html(base_url + brand_url)
        doc = html.fromstring(html_content)
        type_elements = doc.xpath('//ul[@class="partsubselect"]//li/a')
        for type_element in type_elements:
            href = type_element.get('href')  # Get the URL (href attribute)
            text = type_element.text  # Get the text content of the <a> tag

            try:
                type_content = fetch_html(base_url + href)
                type_doc = html.fromstring(type_content)
                year_elements = type_doc.xpath('//div[@class="halfc"]//li/a')
                for year_element in year_elements:
                    href_year = year_element.get('href')
                    year = year_element.text

                    try:
                        year_content = fetch_html(base_url + href_year)
                        year_doc = html.fromstring(year_content) 
                        brand = extract_by_xpath(year_doc, '//*[@id="partsselectlist"]/div[1]/ul/li[2]/a/span')
                        type = extract_by_xpath(year_doc, '//*[@id="partsselectlist"]/div[1]/ul/li[3]/a/span')
                        year = extract_by_xpath(year_doc, '//*[@id="partsselectlist"]/div[1]/ul/li[4]/a/span')
                        model_elements = year_doc.xpath('//ul[@class="partsubselect columnlist columnlist_33"]//li/a')
                        for model_element in model_elements:
                            url = base_url + model_element.get('href')
                            model = model_element.text
                            save_to_csv([brand, type, year, model, url], csv_file)
                    except Exception as e:
                        print(f"Skipping year URL due to error: {e}")
            except Exception as e:
                print(f"Skipping type URL due to error: {e}")
        print("ended successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
