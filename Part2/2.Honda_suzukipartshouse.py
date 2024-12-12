from datetime import datetime
import requests
from lxml import html
import csv
import sys
import time

def fetch_html(url):
    max_retries = 5
    retries = 0
    retry_delay=5
    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.content  # Return content if successful
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}. Retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)  # Wait before retrying

    print(f"Failed to fetch URL {url} after {max_retries} attempts. Exiting.")
    sys.exit(1)

def extract_by_xpath(doc, xpath):
    """
    Extract the data from the HTML document using the provided XPath.
    """
    try:
        elements = doc.xpath(xpath)
        if elements:
            return elements[0].text.strip()
        else:
            raise ValueError("Element not found for the given XPath.")
    except Exception as e:
        print(f"Error extracting data using XPath '{xpath}': {e}")
        return None

def save_to_csv(data, file_name):
    """
    Save the data to a CSV file, ensuring all fields are quoted.
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
    except FileNotFoundError:
        print("Error: key.csv not found.")
        return
    except Exception as e:
        print(f"Error reading key.csv: {e}")
        return

    base_url = "https://www.babbittsonline.com"
    input_file = "result_part1/2_honda_suzukipartshouse_1_20241203125200.csv"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_file = f"csv/2_Honda_Suzukipartshouse_2_{timestamp}.csv"

    print("Started!")
    save_to_csv(["Brand", "Type", "Year", "Model", "Diagram Name", "Ref #", "Part description", "Part number", "OEM diagram URL", "Price", "SSPN"], csv_file)

    try:
        with open(input_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                if row_number < 4351:
                    continue
                if row_number >= 4464:
                    continue
                print(row_number)
                if len(row) < 5:
                    print(f"Skipping invalid row in input file at line {row_number}: {row}")
                    continue

                brand = row[0]
                type = row[1]
                year = row[2]
                model = row[3]
                model_url = row[4]

                model_content = fetch_html(model_url)
                if not model_content:
                    continue

                model_doc = html.fromstring(model_content)
                model_elements = model_doc.xpath('//div[@class="passemname"]//a')
                
                for model_element in model_elements:
                    try:
                        diagram_href = model_element.get('href')
                        diagram_name = model_element.text
                        if (brand.upper(), diagram_name.upper()) not in diagram_dict:
                            continue

                        oem_diagram_url = base_url + diagram_href
                        diagram_content = fetch_html(base_url + diagram_href)
                        if not diagram_content:
                            continue

                        diagram_doc = html.fromstring(diagram_content)
                        ref_elements = diagram_doc.xpath('//div[@class="partlistrow"]//form')

                        for ref_element in ref_elements:
                            try:
                                ref = ref_element.xpath('.//div[@class="c0"]/span')[0].text.strip()
                                part_description = ref_element.xpath('.//div[@class="c1a"]/span')[0].text.strip()
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

                            except IndexError as e:
                                print(f"Error extracting data from ref_element in line {row_number}: {e}")
                            except Exception as e:
                                print(f"Unexpected error processing ref_element in line {row_number}: {e}")
                    except Exception as e:
                        print(f"Error processing diagram element in line {row_number}: {e}")
    except FileNotFoundError:
        print("Error: Input CSV file not found.")
    except Exception as e:
        print(f"Error reading input file: {e}")

if __name__ == "__main__":
    main()
