import certifi
import requests
from bs4 import BeautifulSoup
import time
from urllib3.exceptions import InsecureRequestWarning
import json

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_data_json():
    try:
        # regions = (12:'Mariy El', 77:'Moscow', 21:'Chuvashiya', 58:'Penza', 91:'Krum')
        url = "https://torgi.gov.ru/new/api/public/lotcards/search?subjRF=91&lotStatus=APPLICATIONS_SUBMISSION&catCode=11&withFacets=true&size=5&sort=updateDate,desc"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "application/json, text/plain, */*",
        }
        count = 0
        while True:
            count += 1
            print(count)
            result = requests.get(url, headers=headers, verify=False).json();
            time.sleep(5)

            with open("torgi/result.json", "a", encoding='utf8') as file:
                    json.dump(result["content"], file, ensure_ascii=False, indent=4)
            if (result["last"]):
                break
            else:
                pageN = result["number"]+1
                url = f"https://torgi.gov.ru/new/api/public/lotcards/search?subjRF=91&lotStatus=APPLICATIONS_SUBMISSION&catCode=11&withFacets=true&page={pageN}&size=5&sort=updateDate,desc"

    except Exception as _ex:
        print(_ex)

def get_primary_process(file_path):
    pass

def main():

    #get_data_json()
    print(get_primary_process(file_path="torgi/result.json"))
    # print(get_data(file_path="file_path"))


if __name__ == "__main__":
    main()