import requests
import os
import time
import math
from common.utils import save_as_json

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"}

class Vivino:
    def __init__(self, params, max_page=50):
        self.base_url = "https://www.vivino.com/api/explore/explore"
        self.params = params
        self.headers = HEADERS
        self.output_path = "data"
        self.page_count = 0
        self.max_page = max_page
        
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
            time.sleep(20)
            total_records, records_per_page = self.get_count_and_page()
        if total_records and records_per_page:
            self.page_count = min(math.ceil(total_records / records_per_page), self.max_page)
            print("Total {} records and {} records per page. The script is going to call api {} times.\n".format(
                total_records,
                records_per_page, self.page_count))
        if self.page_count == 0:
            print('No records!')
            return 
        print("Starting...\n")
        result_string_list = ["{"]
        for page in range(self.page_count):
            print("The scraper is working on page {}...\n".format(page))
            single_page_result = self.api_scrape_once()
            if page != 0:
                result_string_list.append(", ")
            result_string_list.append('"Page{}":'.format(page))
            result_string_list.append(single_page_result)
            time.sleep(3)
        result_string_list.append("}")
        save_as_json(''.join(result_string_list), self.output_path, output_name)
        print("Result has been saved to {}\n".format(os.path.join(
            self.output_path, output_name)))




output_name = "{}_data_{}_{}.json"

partitions = [0, 70, 80, 90, 100, 120, 150, 200, 350, 600, 100000]

regions = requests.get('https://www.vivino.com/api/regions', headers=HEADERS).json()

for region in regions['regions'][166:]:
    region_name = region['seo_name']
    price_min = 0
    price_max = 100000
    print('Scraping region {}...'.format(region_name))
    all_params = {
            "country_code": "fr",
            "region_ids[]": [region['id']],
            "currency_code": "SGD",
            "grape_filter": "varietal",
            "min_rating": "1",
            "order_by": "ratings_count",
            "order": "desc",
            "page": 1,
            "price_range_max": price_max,
            "price_range_min": price_min,
            "wine_type_ids[]": [1, 2, 3, 4, 7, 24]
        }
    count, _ = Vivino(all_params).get_count_and_page()
    if count == 0:
        time.sleep(2)
        continue
    if count < 10000:
        output_file_name = output_name.format(region_name, price_min, price_max)
        print("Total count: {}, starting the scraper for all partitions".format(count))
        Vivino(all_params).api_scrape_all(output_file_name)
        time.sleep(10)
    else:  
        # print("Total count: {}".format(count))
        # for p in range(len(partitions) - 1):
        #     price_min = partitions[p]
        #     price_max = partitions[p + 1]
        #     all_params["price_range_min"] = price_min
        #     all_params["price_range_max"] = price_max
        #     output_file_name = output_name.format(region_name, price_min, price_max)
        # print("Starting the scraper for partition with price from {} to {}".format(price_min, price_max))
        output_file_name = output_name.format(region_name, price_min, price_max)
        Vivino(all_params, 80).api_scrape_all(output_file_name)
        time.sleep(5)


