import certifi
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib3.exceptions import InsecureRequestWarning
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
import re
from win32com import client
from os import path

MIN_AREA = 10
BIDD_TYPE = {
    "229FZ":"Должников",
    "1041PP":"Государственное",
    "178FZ":"Муниципальное"
}
MAX_PRICE = 10000000
MIN_PRICE = 500000
MIN_PRICE_ROOM_M2 = 5000

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
            result = requests.get(url, headers=headers, verify=False).json();
            time.sleep(5)
            print(count, "/", result['totalPages'])
            with open(f"torgi/result/result_{count}.json", "w", encoding='utf8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=4)
            if (result["last"]):
                return count
            else:
                time.sleep(random(3,10))
                pageN = result["number"]+1
                url = f"https://torgi.gov.ru/new/api/public/lotcards/search?subjRF={subjRF}&biddType={biddType}&lotStatus=APPLICATIONS_SUBMISSION&catCode=11&withFacets=true&page={pageN}&size=10"

    except Exception as _ex:
        print(_ex)

def extract_cadastral_num(obj):
    cad_pattern = re.compile(
        r'(,\s+)?(:?кад\. №|кадастро\w+ н\w+|кадастровый №|с кадастровым номером|\():?\s*(?P<cad>([\d:]{14,19}[,;]?\s*)+)',
        flags=re.IGNORECASE)
    match = cad_pattern.search(obj['lotName'])
    cad = None
    if match:
        cad = match["cad"]
        obj['lotName'] = cad_pattern.sub('', obj['lotName'])

    return cad

def transform_into_flatter_structure(amount_files):
    data = {}
    data["content"] = []

    for i in range(1, amount_files + 1):
        with open(f"torgi/result/result_{i}.json", encoding='utf8') as f:
            json_data = json.load(f)
            for i in json_data['content']:

                characteristics = {}
                for characteristic in i['characteristics']:
                    characteristics[characteristic['name']] = characteristic[
                        'characteristicValue'] if "characteristicValue" in characteristic else None

                total_area = characteristics.get('Общая площадь')
                #удаляем инфу про площадь общ. пл.
                area_pattern = re.compile(r'(,\s+)?(:?(общ(\w+)\s+)?площад\w+|общ\. ?пл\.).{1,20}(\((\w+\s+)+\w+\)\s*)?кв(\.|адратных)\s*м(:?\b|етров\b)', flags=re.IGNORECASE)
                if not total_area:
                    total_area = area_pattern.search(i['lotName'])
                i['lotName'] = area_pattern.sub('', i['lotName'])

                # if total_area < MIN_AREA:
                #     continue
                bad_words = re.compile(r'(:? дол[ия]\b|\bгараж|машино-?место|\bподвал|\bподпол|\bчерда\w+)', flags=re.IGNORECASE)
                if bad_words.search(i['lotName']):
                    continue

                price = i['priceMin']
                # if MIN_PRICE > price or price > MAX_PRICE:
                #     continue

                price_m2 = float(price) / float(total_area)
                # if MIN_PRICE_ROOM_M2 > price_m2:
                #     continue

                bidd_type = BIDD_TYPE.get(i['biddType']['code']) or i['biddType']['code']

                cadastral = extract_cadastral_num(i)
                if not cadastral:
                    cadastral = characteristics.get('Кадастровый номер')  or  characteristics.get(
                        'Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение') or None
                #удаляем лишнюю инфу про тип аукциона
                excess_pattern = re.compile(r',?\s*(посредством публичного предложения|без объявления цены|\([,\.\s]*\))\.?', flags=re.IGNORECASE)
                i['lotName'] = excess_pattern.sub('', i['lotName'])

                #удаляем адрес и сохраняем в отдельном
                address_pattern = re.compile(r'(:?(,\s+)?(:?расположен\w+|находящееся)? по адресу|местоположение):?\s*(?P<address>.+)$', flags=re.IGNORECASE)
                match = address_pattern.search(i['lotName'])
                if match:
                    address = match["address"]
                else:
                    address_pattern = re.compile(r'(?P<address>(:?г\.|город|по ул\.|по улице).+)$',
                        flags=re.IGNORECASE)
                    match = address_pattern.search(i['lotName'])
                    address = match["address"] if match else None

                if address:
                    selo_pattern = re.compile(r',\s*\b(с\.|п\.|пос\.|село|поселок|д\.\s*[а-я]+|деревня)\s+.+[,\.$]]',
                                              flags=re.IGNORECASE)
                    match = selo_pattern.search(address)
                    if match:
                        # continue
                        print(match[0])

                i['lotName'] = address_pattern.sub('', i['lotName'])

                object = {
                    "Регион": i['subjectRFCode'],
                    "Общая площадь": total_area,
                    "id": f"""=HYPERLINK("https://torgi.gov.ru/new/public/lots/lot/{i['id']}/(lotInfo:info)", "{i['id']}")""",
                    "Название": i['lotName'],
                    "Цена за кв.м": price/total_area,
                    "Цена": price,
                    "Адрес": address,
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d %m %y %H:%M"),
                    "Кадастровый номер": cadastral, #characteristics['Кадастровый номер'],
                    "Кадастровая стоимость": characteristics.get('Кадастровая стоимость '),
                    "Форма проведения": i['biddForm']['code'],
                    "Имущество": bidd_type
                }
                data["content"].append(object)

    with open(f"torgi/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
def install_setting_of_columns(writer):
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.autofilter('A1:B100')
    currency_format = workbook.add_format({'num_format': '# ### ##0 ₽'})
    format_area = workbook.add_format({'num_format': '# ##0,0\ \м2'})
    format_name = workbook.add_format()
    format_name.set_font_color('blue')
    format_name.set_underline()

   # (max_row, max_col) = df.shape
    #max_row = worksheet.get_highest_row()
    # Регион
    worksheet.set_column('B:B', 3)
    # area
    worksheet.set_column('C:C', 9, format_area)

    # name
    worksheet.set_column('D:D', 20, format_name)
    worksheet.set_column('E:E', 40)
    worksheet.set_column('H:H', 40)
    worksheet.set_column('I:I', 12)
    worksheet.set_column('J:J', 18)
    # price
    worksheet.set_column('F:G', 12, currency_format)
    worksheet.set_column('K:K', 12, currency_format)
    #
    # red = workbook.add_format({'bg_color': '#FFC7CE',
    #                                'font_color': '#9C0006'})
    green = workbook.add_format({'bg_color': '#C6EFCE',
                                 'font_color': '#006100'})

    worksheet.conditional_format('L1:L1000', {'type': 'text',
                                                    'criteria': 'containsText',
                                                    'value': "PP",
                                                    'format': green})

def save_opening_output_file(file_path):
    excelApp = client.Dispatch("Excel.Application")
    excelApp.DisplayAlerts = False
    book = excelApp.Workbooks.open(path.abspath(file_path))
    book.Save()
    book.Close()

def primary_processing(path_file):
    with open("torgi/result_full.json", encoding='utf8') as f:
        json_data = json.load(f)
        df = json_normalize(json_data['content'])

        #что бы можно было оставлять открым файл оутпут
        save_opening_output_file('torgi/output.xlsx')

        with pd.ExcelWriter('torgi/output.xlsx',  engine='xlsxwriter', mode="w") as writer:

            df.to_excel(writer,  encoding='utf-8')
            install_setting_of_columns(writer)

def main():
    #subjRF = (12:'Mariy El', 77:'Moscow', 21:'Chuvashiya', 58:'Penza', 91:'Krum')
    # biddType="229FZ":"Должников","1041PP":"обращенного в собственноcть государства","178FZ":"государсвенного и муниципального имущества"

    #amaount_files = get_data_json(subjRF="12,21,16,58,91,77", biddType="229FZ,1041PP,178FZ")
   # print(amaount_files)
    transform_into_flatter_structure(26)
    primary_processing("torgi/result_full.json")


if __name__ == "__main__":
    main()