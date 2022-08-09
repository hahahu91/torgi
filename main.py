import certifi
import requests
from bs4 import BeautifulSoup
import time
import random
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
import re
from win32com import client
from os import path
from population_in_district import get_commercial_assessment
from get_coord import get_location, get_info_object
from get_address import get_address

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import os


# Suppress only the single warning from urllib3 needed.
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


MIN_AREA = 10
BIDD_TYPE = {
    "229FZ":"Должников",
    "1041PP":"Государственное",
    "178FZ":"Муниципальное"
}
MAX_PRICE = 10000000
MIN_PRICE = 500000
MIN_PRICE_ROOM_M2 = 1000

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_data_json(bidd_type, subj_rf="", lot_status="APPLICATIONS_SUBMISSION", folder="torgi/result"):
    try:
        if not lot_status:
            lot_status = "APPLICATIONS_SUBMISSION"
        #page_n
        #url = f"https://torgi.gov.ru/new/api/public/lotcards/search?subjRF={subj_rf}&biddType={bidd_type}&lotStatus={lot_status}&catCode=11&withFacets=true{page_n}&size=25&sort=updateDate,desc"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "application/json, text/plain, */*",
        }
        count = 0
        while True:
            count += 1
            page_n = "" if count == 1 else f"&page={result['number'] + 1}"
            str_subj_rf = f"subjRF={subj_rf}&" if subj_rf else ""
            url = f"https://torgi.gov.ru/new/api/public/lotcards/search?{str_subj_rf}biddType={bidd_type}&chars=&chars=dec-totalAreaRealty:10~&lotStatus={lot_status}&catCode=11&withFacets=true{page_n}&size=25&sort=updateDate,desc"
            result = requests.get(url, headers=headers, verify=False).json();
            if not result:
                print("not get url")
                return

            print("get page ", count, "/", result['totalPages'])
            with open(f"{folder}/result_{count}.json", "w", encoding='utf8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=4)
            if (result["last"]):
                return count
            else:
                time.sleep(random.randint(5,20))

    except Exception as _ex:
        print(_ex)

def extract_cadastral_num(obj):
    cad_pattern = re.compile( #кадастровый (условный) номер
        #r'(,\s+)?(:?кад\. №|кадастро\w+ н\w+|кадастровый №|с кадастровым номером|\(|кадастровый( (или )?условный)? номер объекта):?\s*(?P<cad>([\d:]{14,19}[,;]?\s*)+)',
        r'(,\s+)?(:?(с )?(кад\.|кадастро\w+|кн|к\/н|к\.н\.|cad)( ?\((или )?условный\))? ?(:?№|н\w+|ном\.|н\.)( об\w*\.?| помещ\w+)?|\():?\s*(?P<cad>(\d{2}\s*:\s*\d{2}\s*:\s*\d{4,8}\s*:\s*\d{1,5}[,;]?\s*)+)', flags=re.IGNORECASE)
    match = cad_pattern.search(obj['lotDescription']) or cad_pattern.search(obj['lotName'])
    cad = None
    # if not match:
    #     match = cad_pattern.search(obj['lotName'])
    if match:
        cad = match["cad"]
        obj['lotDescription'] = cad_pattern.sub('', obj['lotDescription'])

    return cad


def transform_into_flatter_structure(folder="torgi/result"):
    amount_files = 0
    for i in os.listdir(f"{folder}/"):
        if i != 'result_full.json':
            amount_files += 1

    data = {}
    data["content"] = []

    for j in range(1, amount_files + 1):
        # if j == 4:
        #     break
        with open(f"{folder}/result_{j}.json", encoding='utf8') as f:
            json_data = json.load(f)
            count = 0
            for i in json_data['content'][:]:
                # if i == 2:
                #     break
                count += 1
                print(f"processing object {count}/{len(json_data['content'])} in file {j}/{amount_files}")
                characteristics = {}
                for characteristic in i['characteristics']:
                    characteristics[characteristic['name']] = characteristic[
                        'characteristicValue'] if "characteristicValue" in characteristic else None
                # if i['lotName'] not in i['lotDescription']:
                #     i['lotDescription'] = f"{i['lotName']}, {i['lotDescription']}"

                #удаляем инфу про площадь
                area_pattern = re.compile(r'(,\s+)?(:?(общ(\w+)\s+)?площад\w+|общ\. ?пл\.)\D{1,20}(?P<area>[\d,.\s]+\d+)\s*(\(([^\d\W]+\s+)+[^\d\W]+\)\s*)?кв(\.|адратных)\s*м(:?\b|етров\b)', flags=re.IGNORECASE)
                match = area_pattern.search(i['lotDescription']) or area_pattern.search(i['lotName'])
                # if not match:
                #     match = area_pattern.search(i['lotName'])
                if match:
                    total_area = float(match['area'].replace(' ', '').replace(',', '.'))
                    i['lotDescription'] = area_pattern.sub('', i['lotDescription'])
                else:
                    total_area = characteristics.get('Общая площадь')

                if total_area < MIN_AREA:
                    continue
                bad_words = re.compile(r'(:? дол[ия]\b|\bгараж|машино-?место|свинарник|(?<!этажа и )\bподвал|\bподпол|\bчерда\w+|картофелехранилище|долевая)', flags=re.IGNORECASE)
                if bad_words.search(i['lotDescription']) or bad_words.search(i['lotName']):
                    continue

                price = i.get('priceFin') or i.get('priceMin')
                if MIN_PRICE > price or price > MAX_PRICE:
                    continue

                price_m2 = price / total_area
                if MIN_PRICE_ROOM_M2 > price_m2:
                    continue

                bidd_type = BIDD_TYPE.get(i['biddType']['code']) or i['biddType']['code']

                cadastral = extract_cadastral_num(i)
                if not cadastral:
                    cadastral = characteristics.get('Кадастровый номер')  or  characteristics.get(
                        'Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение') or None
                #удаляем лишнюю инфу про тип аукциона
                excess_pattern = re.compile(r',?\s*(:?посредством публичного предложения|без объявления цены|\([,\.\s]*\))\.?', flags=re.IGNORECASE)
                i['lotDescription'] = excess_pattern.sub('', i['lotDescription'])

                #удаляем адрес и сохраняем в отдельном
                address = get_address(i['lotDescription']) or get_address(i['lotName'])
                if address:
                    try:
                        i['lotDescription'] = re.sub(re.escape(address), '', i['lotDescription'])
                    except Exception as _ex:
                        print(_ex)
                        print(i['lotDescription'], address)
                if address or cadastral:
                    print(i['id'])
                    info_object = get_info_object(i['id'], address, cadastral)
                lat, lon = None, None
                if info_object:
                        lat = info_object["lat"]
                        lon = info_object["lon"]
                        address = info_object["address"]
                #commercial_assessment = 0
                # if lat and lon and i.get('subjectRFCode'):
                #     try:
                #         commercial_assessment = get_commercial_assessment(lat, lon, i['subjectRFCode'])
                #     except Exception as _ex:
                #         print(_ex, "\r\n", lat, lon, i['subjectRFCode'])
                # residents = 0
                # shops = 0
                # if commercial_assessment:
                #     residents = commercial_assessment.get("residents")
                #     for category  in commercial_assessment:
                #         if category != "residents":
                #             shops += commercial_assessment.get(category)
                coord = f'''=HYPERLINK("https://yandex.ru/maps/?&text={lat}, {lon}", "{lat}, {lon}")''' if lat and lon and lat != "None" and lon != "None" else ""
                object = {
                    "Регион": i['subjectRFCode'],
                    "Общая площадь": total_area,
                    "id": f"""=HYPERLINK("https://torgi.gov.ru/new/public/lots/lot/{i['id']}/(lotInfo:info)", "{i['id']}")""",
                    "Название": i['lotDescription'],
                    "Цена за кв.м": price_m2,
                    "Цена": price,
                    "Адрес": address,
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d %m %y %H:%M"),
                    "Кадастровый номер": cadastral, #characteristics['Кадастровый номер'],
                    "Cтоимость чел/кв.м": "",
                    "Форма проведения": i['biddForm']['code'],
                    "Имущество": re.sub(r"^(.).+$", r"\1", bidd_type),
                    "Координаты": coord,
                    "Жителей в округе": "",
                    "Коммерческих объектов": "",
                    "Описание коммерческих объектов": ""
                }
                data["content"].append(object)

    with open(f"{folder}/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{folder}/result_full.json"


def install_setting_of_columns(writer):
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.autofilter('A1:B100')
    currency_format = workbook.add_format({'num_format': '# ### ##0 ₽'})
    format_area = workbook.add_format({'num_format': '# ##0.0 м2'})
    format_hyper = workbook.add_format({'font_color': 'blue', 'underline': True})

   # (max_row, max_col) = df.shape
    #max_row = worksheet.get_highest_row()
    # Регион
    worksheet.set_column('B:B', 3)
    # area
    worksheet.set_column('C:C', 9, format_area)

    # name
    worksheet.set_column('D:D', 22, format_hyper)
    worksheet.set_column('N:N', 22, format_hyper)
    worksheet.set_column('Q:Q', 22, format_hyper)
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
    if path.exists(file_path):
        excelApp = client.Dispatch("Excel.Application")
        book = excelApp.Workbooks.open(path.abspath(file_path))
        excelApp.DisplayAlerts = False
        book.Save()
        book.Close()

def primary_processing(path_file):
    with open(path_file, encoding='utf8') as f:
        json_data = json.load(f)
        df = json_normalize(json_data['content'])
        #mat
        out_file="torgi/output.xlsx" if path_file.find("archive") == -1 else "torgi/output_archive.xlsx"
        try:
            #что бы можно было оставлять открым файл оутпут
            save_opening_output_file(out_file)
        except Exception as _ex:
            print(_ex)

        with pd.ExcelWriter(out_file,  engine='xlsxwriter', mode="w") as writer:
            df.to_excel(writer,  encoding='utf-8')
            install_setting_of_columns(writer)
            return out_file


def visualize_data(path_file):
    with open(path_file, encoding='utf8') as f:
        json_data = json.load(f)
        df = json_normalize(json_data['content'])

        df_debtors = df[df['Имущество'].isin(["Должников"])]
        df_municipal = df[df['Имущество'].isin(["Муниципальное"])]
        x1 = df_debtors['Общая площадь'].to_numpy()
        x2 = df_municipal['Общая площадь'].to_numpy()
        # x = df['Общая площадь'].to_numpy()
        y1 = pd.to_numeric(df_debtors['Цена']).to_numpy()
        y2 = pd.to_numeric(df_municipal['Цена']).to_numpy()
        # plt.plot(df['Общая площадь'], pd.to_numeric(df['Цена']))
        [row1, column1] = df_debtors.shape
        [row2, column2] = df_municipal.shape
        # print(x1)
        # print(y1)

        x1 = x1.reshape(row1, 1)
        y1 = y1.reshape(row1, 1)
        x2 = x2.reshape(row2, 1)
        y2 = y2.reshape(row2, 1)
        regr_debt = LinearRegression()
        regr_debt.fit(x1, y1)
        regr_muni = LinearRegression()
        regr_muni.fit(x2, y2)
        #
        # # plot it as in the example at http://scikit-learn.org/
        #plt.subplot(2, 1, 1)
        plt.scatter(x1, y1, color='green')
        plt.plot(x1, regr_debt.predict(x1), color='green', linewidth=2)
        # plt.xticks(())
        # plt.yticks(())
        #plt.subplot(2, 1, 2)
        plt.scatter(x2, y2, color='red')
        plt.plot(x2, regr_muni.predict(x2), color='red', linewidth=2)
        # plt.xticks(())
        # plt.yticks(())
        plt.show()

def main():
    #subjRF = (12:'Mariy El', 50:'MoscowOblast', 77:'Moscow', 21:'Chuvashiya', 58:'Penza', 91:'Krum') subj_rf="12,21,16,58,91,77,50"
    # biddType="229FZ":"Должников","1041PP":"обращенного в собственноcть государства","178FZ":"государсвенного и муниципального имущества"
    #lotStatus=SUCCEED сбор завершенных данных; status = "APPLICATIONS_SUBMISSION прием заявок

    #status = "APPLICATIONS_SUBMISSION"
    status = "SUCCEED"
    folder = "torgi/result" if status != "SUCCEED" else "torgi/archive" #12,21,16,58,91,77,50

    amount_files = get_data_json(bidd_type="229FZ,1041PP,178FZ", subj_rf="",  lot_status=status, folder=folder)
   # # print(amount_files)
    path = transform_into_flatter_structure(folder=folder)
    primary_processing(path)
    #visualize_data(path)

if __name__ == "__main__":
    main()