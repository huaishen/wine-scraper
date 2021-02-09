import requests
import os
import time
from common.utils import save_as_json
 
class Vivino:
    def __init__(self, params, output_name):
        self.base_url = "https://www.vivino.com/api/explore/explore"
        self.params = params
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"}
        self.output_path = "data"
        self.output_name = output_name 
    
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
    

    
    def api_scrape_all(self):
        total_records, records_per_page = self.get_count_and_page()
        if total_records and records_per_page:
            page_count = int(total_records / records_per_page) + 1
            print("Total {} records and {} records per page. The script is going to call api {} times.\n".format(total_records,
                  records_per_page, page_count))
        print("Starting...\n")
        result_string_list = ["{"]
        for page in range(page_count):
            print("The scraper is working on page {}...\n".format(page))
            single_page_result = self.api_scrape_once()
            if page != 0:
                result_string_list.append(", ")
            result_string_list.append('"Page{}":'.format(page))
            result_string_list.append(single_page_result)
            time.sleep(1)
        result_string_list.append("}")
        save_as_json(''.join(result_string_list), self.output_path, self.output_name)
        print("Result has been saved to {}".format(os.path.join(
            self.output_path, self.output_name)))
        
            
        
    
        


sg_all_params = {
    "country_code": "SG",
    "currency_code": "SGD",
    "grape_filter": "varietal",
    "min_rating": "1",
    "order_by": "price",
    "order": "asc",
    "page": 200,
    "price_range_max": "600",
    "price_range_min": "0",
    "wine_type_ids[]": ["1", "2", "3", "4", "7", "24"]
}
output_name = "test1.json"

result = Vivino(sg_all_params, output_name).call_api().json()

