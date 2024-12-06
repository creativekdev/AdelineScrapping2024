from datetime import datetime
import requests
from lxml import html
import csv

def fetch_html(url):
    """
    Fetch HTML content from a URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_by_xpath(doc, xpath):
    """
    Extract content from the HTML document using the provided XPath.
    """
    try:
        elements = doc.xpath(xpath)
        if elements:
            return elements[0].text.strip()
        else:
            raise ValueError("Element not found for the provided XPath.")
    except (IndexError, ValueError) as e:
        print(f"Error extracting data using XPath '{xpath}': {e}")
        return ""

def save_to_csv(data, file_name):
    """
    Save data to a CSV file, ensuring all fields are quoted.
    """
    try:
        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            writer.writerow(data)
    except IOError as e:
        print(f"Error writing to CSV file {file_name}: {e}")

def main():
    diagram_dict = {}
    diagram_content_dict = {}

    try:
        with open('key.csv', mode='r', encoding='utf-8') as key_file:
            reader = csv.reader(key_file)
            for row in reader:
                if len(row) < 3:
                    print(f"Skipping invalid row in key.csv: {row}")
                    continue
                brand = row[0]
                diagram_name = row[1]
                part_description = row[2]

                diagram_dict[(brand.upper(), diagram_name.upper())] = 1
                diagram_content_dict[(brand.upper(), diagram_name.upper(), part_description.upper())] = 1
    except IOError as e:
        print(f"Error reading key.csv: {e}")
        return

    base_url = "https://www.babbittsonline.com"
    input_file = "result_part1/8_Kawasaki_1_20241203192745.csv"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_file = f"csv/8_Kawasaki_2_{timestamp}.csv"

    print("Started!")
    save_to_csv(["Brand", "Type", "Year", "Model", "Diagram Name", "Ref #", "Part description", "Part number", "OEM diagram URL", "Price", "SSPN"], csv_file)

    try:
        with open(input_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                if row_number == 1:
                    continue
                if len(row) < 5:
                    print(f"Skipping incomplete row {row_number} in input file: {row}")
                    continue

                brand, type, year, model, model_url = row

                model_content = fetch_html(model_url)
                if model_content is None:
                    continue

                model_doc = html.fromstring(model_content)
                model_elements = model_doc.xpath('//div[@class="passemname"]//a')
                for model_element in model_elements:
                    diagram_href = model_element.get('href')
                    diagram_name = model_element.text
                    if not diagram_href or (brand.upper(), diagram_name.upper()) not in diagram_dict:
                        continue

                    oem_diagram_url = base_url + diagram_href
                    diagram_content = fetch_html(base_url + diagram_href)
                    if diagram_content is None:
                        continue

                    diagram_doc = html.fromstring(diagram_content)
                    ref_elements = diagram_doc.xpath('//div[@class="partlistrow"]//form')
                    for ref_element in ref_elements:
                        try:
                            ref = extract_by_xpath(ref_element, './/div[@class="c0"]/span')
                            part_description = extract_by_xpath(ref_element, './/div[@class="c1a"]/span')

                            price_elements = ref_element.xpath('.//div[@class="c2"]/span')
                            price = price_elements[0].text.strip().replace("$", "") if price_elements else ""

                            part_numbers = ref_element.xpath('.//div[@class="c1b"]/a/span')
                            if len(part_numbers) >= 2:
                                part_number = part_numbers[0].text.strip()
                                sspn = part_numbers[1].text.strip()
                                save_to_csv([brand, type, year, model, diagram_name, ref, part_description, part_number, oem_diagram_url, price, sspn], csv_file)
                                save_to_csv([brand, type, year, model, diagram_name, ref, part_description, sspn, oem_diagram_url, price, part_number], csv_file)
                            else:
                                part_number = part_numbers[0].text.strip()
                                sspn = ""
                                save_to_csv([brand, type, year, model, diagram_name, ref, part_description, part_number, oem_diagram_url, price, sspn], csv_file)

                        except (IndexError, ValueError) as e:
                            print(f"Error processing part element: {e}")
    except IOError as e:
        print(f"Error reading input file {input_file}: {e}")

    print("Ended!")

if __name__ == "__main__":
    main()