# import certifi
# import requests
# from bs4 import BeautifulSoup
# import time
# import random
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime
import re
from win32com import client
from os import path
from get_data import get_data_from_torgi_gov, get_address_from_full_data
from population_in_district import get_objs_in_district_from_cache
from population_from_h3 import get_residents_from_cache_h3
from get_coord import get_location, get_info_object
from get_address import get_address
from test import get_from_kontur_population, get_population_from_osm

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import os



MIN_AREA = 10
BIDD_TYPE = {
    "229FZ":"Должников",
    "1041PP":"Государственное",
    "178FZ":"Муниципальное"
}
SUBJ_RF = {  12:'Mariy El',
            16:'Tatarstan',
            21:'Chuvashiya',
            50:'Moscow Oblast',
            58:'Penza',
            77:'Moscow',
            91:'Krum',
            92:'Sevastopol'
        }#2,21,16,58,91,77,50,92
MAX_PRICE = 10000000
MIN_PRICE = 500000
MIN_PRICE_ROOM_M2 = 1000

# Suppress only the single warning from urllib3 needed.
#requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def get_cadastral_num(obj):
    cad_pattern = re.compile( #кадастровый (условный) номер
        #r'(,\s+)?(:?кад\. №|кадастро\w+ н\w+|кадастровый №|с кадастровым номером|\(|кадастровый( (или )?условный)? номер объекта):?\s*(?P<cad>([\d:]{14,19}[,;]?\s*)+)',
        r'(,\s+)?(:?(с )?(кад\.|кадастро\w+|кн|к\/н|к\.н\.|cad)( ?\((или )?условный\))? ?(:?№|н\w+|ном\.|н\.)( об\w*\.?| помещ\w+)?|\():?\s*(?P<cad>(\d{2}\s*:\s*\d{2}\s*:\s*\d{4,8}\s*:\s*\d{1,5}[,;]?\s*)+)', flags=re.IGNORECASE)
    match = cad_pattern.search(obj['lotDescription']) or cad_pattern.search(obj['lotName'])

    cad = match["cad"] if match else None
    # if match:
    #     cad = match["cad"]
    #     obj['lotDescription'] = cad_pattern.sub('', obj['lotDescription'])

    return cad

def transform_into_flatter_structure(amount_files = None, folder="cache/APPLICATIONS_SUBMISSION"):
    print("transform_into_flatter_structure")
    if not amount_files:
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

                #получаем инфу про площадь
                area_pattern = re.compile(r'(,\s+)?(:?(общ(\w+)\s+)?площад\w+|общ\. ?пл\.)\D{1,20}(?P<area>[\d,.\s]+\d+)\s*(\(([^\d\W]+\s+)+[^\d\W]+\)\s*)?кв(\.|адратных)\s*м(:?\b|етров\b)', flags=re.IGNORECASE)
                match = area_pattern.search(i['lotDescription']) or area_pattern.search(i['lotName'])
                total_area = float(match['area'].replace(' ', '').replace(',', '.')) if match else characteristics.get('Общая площадь')
                #     #i['lotDescription'] = area_pattern.sub('', i['lotDescription'])
                # else:
                #     total_area = characteristics.get('Общая площадь')
                if total_area < MIN_AREA:
                    continue

                bad_words = re.compile(r'(:? дол[ия]\b|долевой|\bгараж|машино-?место|свинарник|(?<!этажа и )\bподвал|\bподпол|\bчерда\w+|картофелехранилище|долевая)', flags=re.IGNORECASE)
                if bad_words.search(i['lotDescription']) or bad_words.search(i['lotName']):
                    continue

                price = i.get('priceFin') or i.get('priceMin')
                if  price < MIN_PRICE or price > MAX_PRICE:
                    continue

                price_m2 = price / total_area
                if price_m2 < MIN_PRICE_ROOM_M2:
                    continue

                bidd_type = BIDD_TYPE.get(i['biddType']['code']) or i['biddType']['code']

                cadastral = get_cadastral_num(i)
                if not cadastral:
                    cadastral = characteristics.get('Кадастровый номер')  or  characteristics.get(
                        'Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение') or None
                #удаляем лишнюю инфу про тип аукциона
                # excess_pattern = re.compile(r',?\s*(:?посредством публичного предложения|без объявления цены|\([,\.\s]*\))\.?', flags=re.IGNORECASE)
                # i['lotDescription'] = excess_pattern.sub('', i['lotDescription'])

                #получаем адрес
                address = get_address(i['lotDescription']) or get_address(i['lotName'])
                if not address:
                    address = get_address_from_full_data(i['id'])

                info_object = {}
                if address or cadastral:
                    #print("get info", i['id'])
                    info_object = get_info_object(i['id'], address, cadastral)
                # lat, lon = None, None
                # if info_object:
                #         address = info_object.get("address")
                #         postal_distance = info_object.get("postal_distance")

                coord = f'''=HYPERLINK("https://yandex.ru/maps/?&text={info_object.get("lat")}, {info_object.get("lon")}", "{info_object.get("lat")}, {info_object.get("lon")}")''' \
                    if info_object.get("lat") and info_object.get("lon") and info_object.get("lat") != "None" and info_object.get("lon") != "None" \
                    else ""
                entity_from_osm = get_objs_in_district_from_cache(info_object.get("lat"), info_object.get("lon"))
                residence_from_h3 = get_residents_from_cache_h3(info_object.get("lat"), info_object.get("lon"))
                object = {
                    "Регион": i['subjectRFCode'],
                    "Общая площадь": total_area,
                    "id": f"""=HYPERLINK("https://torgi.gov.ru/new/public/lots/lot/{i['id']}/(lotInfo:info)", "{i['id']}")""",
                    "Название": i['lotDescription'],
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d %m %y %H:%M"),
                    "Адрес": info_object.get("address") if info_object else address,
                    "Цена": price,
                    "Цена за кв.м": price_m2,
                    "H3 чел/кв.м ": float(format(int(price_m2)/int(residence_from_h3.get("population")), ".2f")) if residence_from_h3.get("population") else "",
                    "Чел/кв.м": float(format(int(price_m2)/int(entity_from_osm.get("residents")), ".2f")) if entity_from_osm.get("residents") else "",
                    "Ком/кв.м": float(format(int(price_m2)/int(entity_from_osm.get("entity")), ".2f")) if entity_from_osm.get("entity") else "",
                    "Жителей h3": residence_from_h3.get("population") if residence_from_h3 else "",
                    "Жителей в округе": entity_from_osm.get("residents") if entity_from_osm else "",
                    "Коммерческих объектов": entity_from_osm.get("entity") if entity_from_osm else "",
                    "Расстояние до почты": info_object.get("postal_distance") if info_object.get("postal_distance") else "",
                    "Форма проведения": i['biddForm']['code'],
                    "Имущество": re.sub(r"^(.).+$", r"\1", bidd_type),
                    "Координаты": coord,
                    "Описание коммерческих объектов": f"""=HYPERLINK("{os.path.abspath("cache/objs_in_district")}/{info_object.get("lat")}_{info_object.get("lon")}.json", "{info_object.get("lat")}_{info_object.get("lon")}.json")""" \
                        if entity_from_osm.get("entity") else "",
                    "Кадастровый номер": cadastral,  # characteristics['Кадастровый номер'],

                }
                data["content"].append(object)

    with open(f"{folder}/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{folder}/result_full.json"

def install_setting_of_columns(writer):
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.autofilter('A1:T1000')
    currency_format = workbook.add_format({'num_format': '# ### ##0 ₽'})
    currency_format_with_penny = workbook.add_format({'num_format': '# ### ##0.0 ₽'})
    format_area = workbook.add_format({'num_format': '# ##0.0 м2'})
    format_distance = workbook.add_format({'num_format': '#\ ##0\ \м'})
    format_hyper = workbook.add_format({'font_color': 'blue', 'underline': True})

   # (max_row, max_col) = df.shape
    #max_row = worksheet.get_highest_row()
    # Регион
    worksheet.set_column('B:B', 3)
    # area
    worksheet.set_column('C:C', 9, format_area)

    worksheet.set_column('D:D', 23, format_hyper)
    worksheet.set_column('S:T', 22, format_hyper)

    # name
    worksheet.set_column('E:E', 12)

    worksheet.set_column('G:G', 40)
    worksheet.set_column('H:H', 12, currency_format)
    worksheet.set_column('F:F', 12)
    worksheet.set_column('M:O', 5)
    worksheet.set_column('U:U', 12)
    worksheet.set_column('P:P', 7, format_distance)
    worksheet.set_column('Q:R', 3)
    #worksheet.set_column('T:T', 18)
    # price
    #worksheet.set_column('I:K', 9, currency_format)
    worksheet.set_column('I:I', 9, currency_format)
    worksheet.set_column('J:K', 7, currency_format_with_penny)
    worksheet.set_column('L:L', 8, currency_format)
    #
    # red = workbook.add_format({'bg_color': '#FFC7CE',
    #                                'font_color': '#9C0006'})
    green = workbook.add_format({'bg_color': '#C6EFCE',
                                 'font_color': '#006100'})

    worksheet.conditional_format('Q1:Q1000', {'type': 'text',
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
        df['Регион'] = df['Регион'].astype(int)
        df = df.sort_values(by=['Регион', 'Цена за кв.м']).reset_index(drop=True)

        out_file="torgi/output.xlsx" if path_file.find("SUCCEED") == -1 else "torgi/output_archive.xlsx"
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
    #subjRF = (12:'Mariy El', 50:'MoscowOblast',92:'Sevastopol', 77:'Moscow', 21:'Chuvashiya', 58:'Penza', 91:'Krum') subj_rf="12,21,16,58,91,77,50"
    # biddType="229FZ":"Должников","1041PP":"обращенного в собственноcть государства","178FZ":"государсвенного и муниципального имущества"
    #lotStatus=SUCCEED сбор завершенных данных; status = "APPLICATIONS_SUBMISSION прием заявок

    amount_files = None
    status = "APPLICATIONS_SUBMISSION"
    folder = "cache/APPLICATIONS_SUBMISSION" if status != "SUCCEED" else "cache/SUCCEED"
    subj_rf = ','.join(map(str, SUBJ_RF.keys())) if status == 'APPLICATIONS_SUBMISSION' else ""
    bidd_type = '%s' % ",".join(BIDD_TYPE.keys())

    #amount_files = get_data_from_torgi_gov(bidd_type=bidd_type, subj_rf=subj_rf,  lot_status=status, out_folder=folder)

    path = transform_into_flatter_structure(amount_files=amount_files, folder=folder)
    output_file = primary_processing(path)
   # get_from_kontur_population(output_file)
    #get_population_from_osm(output_file)

    #visualize_data(path)

if __name__ == "__main__":
    main()