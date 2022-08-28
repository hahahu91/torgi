import json
import requests
import time
import os
import random
# Suppress only the single warning from urllib3 needed.
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_data_from_torgi_gov(subj_rf="", lot_status="APPLICATIONS_SUBMISSION", out_folder="cache/APPLICATIONS_SUBMISSION"):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    if not lot_status:
        lot_status = "APPLICATIONS_SUBMISSION"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        count = 0
        while True:
            count += 1
            page_n = "" if count == 1 else f"&page={result['number'] + 1}"
            str_subj_rf = f"subjRF={subj_rf}&" if subj_rf else ""
            url = f"https://torgi.gov.ru/new/api/public/lotcards/search?{str_subj_rf}biddType=229FZ,1041PP,178FZ&chars=" \
                  f"&chars=dec-totalAreaRealty:10~&lotStatus={lot_status}&catCode=11&withFacets=true{page_n}&size=25&sort=updateDate,desc"
            result = requests.get(url, headers=headers, verify=False).json();
            if not result:
                print("not get url")
                return

            print("get page ", count, "/", result['totalPages'])
            with open(f"{out_folder}/result_{count}.json", "w", encoding='utf8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=4)
            if (result["last"]):
                return count
            else:
                time.sleep(random.randint(1,10))

    except Exception as _ex:
        print(_ex)

def get_address_from_full_data(id):
    out_folder = "cache/full_data_torgi"
    if os.path.exists(f'{out_folder}/{id}.json'):
        # info_object
        with open(f'{out_folder}/{id}.json', encoding='utf8') as f:
            info_object = json.load(f)
            return info_object.get("estateAddress")
    else:
        try:
            info_object = get_lot_full_data(id, out_folder)
            if info_object:
                return info_object.get("estateAddress")
        except Exception as _ex:
            print(_ex, id)
        return {}

def get_lot_full_data(id, out_folder):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        url = f"https://torgi.gov.ru/new/api/public/lotcards/{id}"
        result = requests.get(url, headers=headers, verify=False).json();
        if not result:
            print("not get url")
            return
        with open(f"{out_folder}/{id}.json", "w", encoding='utf8') as file:
            json.dump(result, file, ensure_ascii=False, indent=4)

        return result

    except Exception as _ex:
        print(_ex)

