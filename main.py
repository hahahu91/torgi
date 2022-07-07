import certifi
import requests
from bs4 import BeautifulSoup
import time
from urllib3.exceptions import InsecureRequestWarning
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
import re

MIN_AREA = 10
BIDD_TYPE = {
    "229FZ":"Должников",
    "1041PP":"Государственное",
    "178FZ":"Муниципальное"
}
MAX_PRICE = 10000000
MIN_PRICE_ROOM = 500000

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_data_json(subjRF,biddType):
    try:
        url = f"https://torgi.gov.ru/new/api/public/lotcards/search?subjRF={subjRF}&biddType={biddType}&lotStatus=APPLICATIONS_SUBMISSION&catCode=11&withFacets=true&size=10"
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

            with open(f"torgi/result_{count}.json", "w", encoding='utf8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=4)
            if (result["last"]):
                return count
            else:
                pageN = result["number"]+1
                url = f"https://torgi.gov.ru/new/api/public/lotcards/search?subjRF={subjRF}&biddType={biddType}&lotStatus=APPLICATIONS_SUBMISSION&catCode=11&withFacets=true&page={pageN}&size=10"

    except Exception as _ex:
        print(_ex)

def transform_into_flatter_structure(amount_files):
    data = {}
    data["content"] = []

    for i in range(1, amount_files + 1):
        with open(f"torgi/result_{i}.json", encoding='utf8') as f:
            json_data = json.load(f)
            for i in json_data['content']:
                total_area = i['characteristics'][0]['characteristicValue']
                # if total_area < MIN_AREA:
                #     continue
                # if " доли " in i['lotName'] or " доля " in i['lotName'] or " гараж" in i['lotName']:
                #     continue

                price = i['priceMin']
                # if MIN_PRICE > price or price > MAX_PRICE:
                #     continue

                try:
                    bidd_type = BIDD_TYPE[i['biddType']['code']]
                except:
                    bidd_type = i['biddType']['code']


                characteristics = {}
                for characteristic in i['characteristics']:
                    if "characteristicValue" in characteristic:
                        characteristics[characteristic['name']] = characteristic['characteristicValue']
                    else:
                        characteristics[characteristic['name']] = None

                #удаляем из названия кадастровый номер и сохраняем его в отдельном столбце
                kad_pattern = re.compile(r',?\s*(:?кад\. №|кадастровый номер|кадастровый №):?\s*([\d+:\d+]+)', flags=re.IGNORECASE)
                match = kad_pattern.search(i['lotName'])
                if match:
                    characteristics['Кадастровый номер'] = match[2]
                    i['lotName'] = kad_pattern.sub('', i['lotName'])
                else:
                    if not characteristics['Кадастровый номер']:
                        if characteristics[ 'Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение']:
                            characteristics['Кадастровый номер'] = characteristics['Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение']

                #удаляем адрес и сохраняем в отдельном
                address_pattern = re.compile(r'(:?(:?расположен\w+|находящееся) по адресу|местоположение):?\s*(?P<address>.+)$', flags=re.IGNORECASE)
                address = address_pattern.search(i['lotName'])
                i['lotName'] = address_pattern.sub('', i['lotName'])

                object = {
                    "id": i['id'],
                    "Регион": i['subjectRFCode'],
                    "Общая площадь": total_area,
                    "Название": i['lotName'],
                    "Цена": price,
                   # "Адрес": address[0],
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d/%m/%y %H:%M"),
                    "Кадастровый номер": characteristics['Кадастровый номер'],
                    "Кадастровая стоимость": characteristics['Кадастровая стоимость '],
                    "Форма проведения": i['biddForm']['code'],
                    "Имущество": bidd_type
                }
                data["content"].append(object)

    with open(f"torgi/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def primary_processing(path_file):
    with open("torgi/result_full.json", encoding='utf8') as f:
        json_data = json.load(f)
        df = json_normalize(json_data['content'])
        with pd.ExcelWriter('torgi/output.xlsx') as writer:
            df.to_excel(writer,  encoding='utf-8')
        # print(df)

def main():
    # subjRF = (12:'Mariy El', 77:'Moscow', 21:'Chuvashiya', 58:'Penza', 91:'Krum')
    # biddType="229FZ":"Должников","1041PP":"обращенного в собственноcть государства","178FZ":"государсвенного и муниципального имущества"

   # amaount_files = get_data_json(subjRF="12,21", biddType="229FZ,1041PP,178FZ")
   # print(amaount_files)
    transform_into_flatter_structure(3)
    primary_processing("torgi/result_full.json")


if __name__ == "__main__":
    main()