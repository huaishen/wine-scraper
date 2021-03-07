import requests
import os
import time
from common.utils import save_as_json


class Vivino:
    def __init__(self, params):
        self.base_url = "https://www.vivino.com/api/explore/explore"
        self.params = params
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"}
        self.output_path = "data"
        self.page_count = 0

    def call_api(self):
        return requests.get(
            self.base_url,
            params=self.params,
            headers=self.headers
        )

    def get_count_and_page(self):
        result = self.call_api()
        try:
            json_result = result.json()
            stats = json_result["explore_vintage"]
            return int(stats["records_matched"]), int(len(stats["matches"]))
        except:
            return 0, None

    def api_scrape_once(self):
        result = self.call_api()
        self.params['page'] += 1
        return result.text

    def api_scrape_all(self, output_name):
        total_records, records_per_page = self.get_count_and_page()
        if not total_records:
            print("")
            time.sleep(30)
            total_records, records_per_page = self.get_count_and_page()
        if total_records and records_per_page:
            self.page_count = int(total_records / records_per_page) + 1
            print("Total {} records and {} records per page. The script is going to call api {} times.\n".format(
                total_records,
                records_per_page, self.page_count))
        print("Starting...\n")
        result_string_list = ["{"]
        for page in range(self.page_count):
            print("The scraper is working on page {}...\n".format(page))
            single_page_result = self.api_scrape_once()
            if page != 0:
                result_string_list.append(", ")
            result_string_list.append('"Page{}":'.format(page))
            result_string_list.append(single_page_result)
            time.sleep(5)
        result_string_list.append("}")
        save_as_json(''.join(result_string_list), self.output_path, output_name)
        print("Result has been saved to {}\n".format(os.path.join(
            self.output_path, output_name)))




output_name = "sg_data_{}_{}.json"

partitions = [70, 80, 90, 100, 120, 150, 200, 350, 600, 10000]

for p in range(len(partitions) - 1):
    sg_all_params = {
        "country_code": "SG",
        "currency_code": "SGD",
        "grape_filter": "varietal",
        "min_rating": "1",
        "order_by": "price",
        "order": "desc",
        "page": 1,
        "price_range_max": 60,
        "price_range_min": 50,
        "wine_type_ids[]": [1, 2, 3, 4, 7, 24]
    }
    price_min = partitions[p]
    price_max = partitions[p + 1]
    sg_all_params["price_range_min"] = price_min
    sg_all_params["price_range_max"] = price_max
    output_file_name = output_name.format(price_min, price_max)
    print("Starting the scraper for partition with price from {} to {}".format(price_min, price_max))
    Vivino(sg_all_params).api_scrape_all(output_file_name)
    time.sleep(60)


