from datetime import datetime
import requests
from lxml import html
import csv

def fetch_html(url):
    """
    Fetch HTML content from a URL with error handling.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None  # Return None if there is an error

def extract_by_xpath(doc, xpath):
    """
    Extract the text from the HTML document using the provided XPath with error handling.
    """
    try:
        elements = doc.xpath(xpath)
        if elements:
            return elements[0].text.strip()
        else:
            raise Exception("Element not found. Check the XPath.")
    except Exception as e:
        print(f"Error extracting data using XPath '{xpath}': {e}")
        return None  # Return None if extraction fails

def save_to_csv(data, file_name):
    """
    Save the data to a CSV file with error handling.
    """
    try:
        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            writer.writerow(data)  # Write data
    except IOError as e:
        print(f"Error writing to CSV file {file_name}: {e}")

def main():
    diagram_dict = {}
    diagram_content_dict = {}

    try:
        with open('key.csv', mode='r', encoding='utf-8') as key_file:
            reader = csv.reader(key_file)
            for row in reader:
                if not row:
                    continue  # Skip empty rows
                brand = row[0]  
                diagram_name = row[1] 
                complete_group = row[2] 
                part_description = row[2] 

                diagram_dict[(brand.upper(), diagram_name.upper())] = 1
                diagram_content_dict[(brand.upper(), diagram_name.upper(), part_description.upper())] = 1
    except FileNotFoundError as e:
        print(f"Error reading key.csv: {e}")
        return  # Stop execution if the key file is missing
    except Exception as e:
        print(f"Unexpected error while reading key.csv: {e}")
        return  # Stop execution for other unexpected errors

    base_url = "https://partsfinder.onlinemicrofiche.com/"
    input_file = "result_part1/4_Suzuki_partsfinder_scooter_1_20241203215648.csv"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_file = f"csv/4_Suzuki_partsfinder_scooter_2_{timestamp}.csv"

    print("Started!")
    save_to_csv(["Brand", "Type", "Year", "Model", "Diagram Name", "Ref #", "Part description", "Part number", "OEM diagram URL", "Price", "SSPN"], csv_file)

    try:
        with open(input_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                if row_number < 60:
                    continue  # Skip header row

                if len(row) < 5:  # Ensure there are enough columns
                    print(f"Skipping row {row_number} due to insufficient columns.")
                    continue

                brand = row[0]
                type = row[1]
                year = row[2]
                model = row[3]
                model_url = row[4]

                model_content = fetch_html(model_url)
                if not model_content:
                    continue  # Skip if content cannot be fetched

                model_doc = html.fromstring(model_content)
                model_elements = model_doc.xpath('//div[@class="SecOneSubSectionRow SecOneSubSectionRow1"]/div')
                for model_element in model_elements:
                    try:
                        diagram_name = model_element.xpath('.//a')[0].text.strip()
                        diagram_href = model_element.xpath('.//a')[1].get('href')
                        if (brand.upper(), diagram_name.upper()) not in diagram_dict:
                            continue

                        oem_diagram_url = diagram_href
                        diagram_content = fetch_html(diagram_href)
                        if not diagram_content:
                            continue  # Skip if content cannot be fetched

                        diagram_doc = html.fromstring(diagram_content)
                        ref_elements = diagram_doc.xpath('//table[@class="parts_list"]//tr')
                        for ref_element in ref_elements:
                            try:
                                part_element = ref_element.xpath('.//td')[2]
                                if len(part_element) == 0:
                                    continue
                                ref = ref_element.xpath('.//td')[1].text.strip() if ref_element.xpath('.//td')[1].text else ""
                                part_description = part_element.xpath('./div')[0].text.strip()

                                price_element = ref_element.xpath('.//td')[3]
                                price = price_element.text.strip() if price_element.text else ""

                                part_number = part_element.xpath('./div')[1].text.strip()
                                sspn = ""

                                save_to_csv([brand, type, year, model, diagram_name, ref, part_description, part_number, oem_diagram_url, price, sspn], csv_file)
                            except Exception as e:
                                print(f"Error processing reference element in row {row_number}: {e}")
                    except Exception as e:
                        print(f"Error processing model element in row {row_number}: {e}")
    except FileNotFoundError as e:
        print(f"Error reading input CSV file {input_file}: {e}")
    except Exception as e:
        print(f"Unexpected error while reading input CSV file: {e}")
    print("Ended!")

if __name__ == "__main__":
    main()
