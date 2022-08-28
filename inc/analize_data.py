import json
from datetime import datetime
import re
import pandas as pd
import numpy as np
import os

from inc.get_data import get_address_from_full_data
from inc.get_coord import get_location, get_info_object, get_locality_population
from inc.parse_data import get_address, get_floor, get_entrance, get_type_object, get_area, get_cadastral_num
from get_population import get_residence
from setting import MIN_AREA,MAX_AREA, MAX_PRICE, MIN_PRICE, MIN_PRICE_ROOM_M2

def transform_into_flatter_structure(amount_files = None, folder="cache/APPLICATIONS_SUBMISSION"):
    print("transform_into_flatter_structure")
    if not amount_files:
        amount_files = 0
        for i in os.listdir(f"{folder}/"):
            if i != 'result_full.json':
                amount_files += 1

    df_population_in_locality = pd.read_excel('konturs/Population.xlsx', usecols=['municipality', 'settlement', 'type', 'population']) #'region',

    data = {}
    data["content"] = []

    for j in range(1, amount_files + 1):
        with open(f"{folder}/result_{j}.json", encoding='utf8') as f:
            json_data = json.load(f)
            count = 0
            for i in json_data['content'][:]:
                count += 1
                print(f"processing object {count}/{len(json_data['content'])} in file {j}/{amount_files}")
                # characteristics = {}
                # for characteristic in i['characteristics']:
                #     characteristics[characteristic['name']] = characteristic[
                #         'characteristicValue'] if "characteristicValue" in characteristic else None
                #получаем инфу про площадь
                # total_area = float(str(characteristics.get('Общая площадь')).replace(' ', '').replace(',', '.')) if characteristics.get('Общая площадь') else None
                # if not total_area:
                #     area_pattern = re.compile(r'(,\s+)?(:?(общ(\w+)\s+)?площад\w+|общ\. ?пл\.)\D{1,20}(?P<area>[\d,.\s]+\d+)\s*(\(([^\d\W]+\s+)+[^\d\W]+\)\s*)?кв(\.|адратных)\s*м(:?\b|етров\b)', flags=re.IGNORECASE)
                #     match = area_pattern.search(i['lotDescription']) or area_pattern.search(i['lotName'])
                #     total_area = float(match['area'].replace(' ', '').replace(',', '.')) if match else 0
                total_area = get_area(i)

                if total_area < MIN_AREA or total_area > MAX_AREA:
                    continue

                bad_words = re.compile(r'(:? дол[ия]\b|\bдолей\b|\bдолями\b|\bдолевой|\bдолевая|свинарник|(?<!не\W)\bжилое помещение\b)', flags=re.IGNORECASE)
                if bad_words.search(i['lotDescription']) or bad_words.search(i['lotName']):
                    continue

                price = i.get('priceFin') or i.get('priceMin')
                if  price < MIN_PRICE or price > MAX_PRICE:
                    continue

                price_m2 = price / total_area
                if price_m2 < MIN_PRICE_ROOM_M2:
                    continue

                floor = get_floor(i)
                if (floor and int(floor) == -1):
                    continue

                type_object = get_type_object(i)
                if type_object in ["подвал","подпол","чердак","гараж"]:
                    continue

                entrance = get_entrance(i)
                legacy = ""
                legacy_pattern  = re.compile(
                    r'(:?культурн\w+ наследи\w+)',
                    flags=re.IGNORECASE)
                if legacy_pattern.search(i['lotDescription']) or legacy_pattern.search(i['lotName']):
                    legacy = 1

                BIDD_TYPE = {
                    "229FZ": "Должников",
                    "1041PP": "Государственное",
                    "178FZ": "Муниципальное"
                }
                bidd_type = BIDD_TYPE.get(i['biddType']['code']) or i['biddType']['code']

                cadastral = get_cadastral_num(i)

                #получаем адрес
                was_full_data = False
                address = get_address(i['lotDescription']) or get_address(i['lotName'])
                if not address:
                    was_full_data = True
                    address = get_address_from_full_data(i['id'])

                info_object = {}
                if address or cadastral:
                    info_object = get_info_object(i['id'], address, cadastral)
                    if not info_object.get('lat') or not info_object.get('lon') and not was_full_data:
                        print(f"get new info {i['id']}")
                        info_object = get_info_object(i['id'],  get_address_from_full_data(i['id']))

                coord = f'''=HYPERLINK("https://yandex.ru/maps/?&text={info_object.get("lat")}, {info_object.get("lon")}", "{info_object.get("lat")}, {info_object.get("lon")}")''' \
                    if info_object.get("lat") and info_object.get("lon") and info_object.get("lat") != "None" and info_object.get("lon") != "None" \
                    else ""
                residence, entity = "", ""
                if info_object.get("lat") and info_object.get("lon"):
                    residence, entity = get_residence(info_object.get("lat"), info_object.get("lon"))

                settlement_population = ""
                settlement_type = info_object.get('settlement_type')
                settlement =  info_object.get('settlement')
                area =  info_object.get('area')
                if settlement_type and settlement:
                    settlement_population = get_locality_population(df=df_population_in_locality, settlement=settlement, settlement_type=settlement_type,  area=area)

                object = {
                    "Регион": i['subjectRFCode'],
                    "Общая площадь": total_area,
                    "id": f"""=HYPERLINK("https://torgi.gov.ru/new/public/lots/lot/{i['id']}/(lotInfo:info)", "{i['id']}")""",
                    "Название": i['lotDescription'],
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d.%m.%y %H:%M"),
                    "Адрес": info_object.get("address") if info_object else address,
                    "Цена": price,
                    "Цена за кв.м": price_m2,
                    "Тип объекта": type_object,#float(format(int(price_m2)/int(residence_from_h3.get("population")), ".2f")) if residence_from_h3.get("population") else "",
                    "Чел/кв.м": float(format(int(price_m2)/int(residence), ".2f")) if residence else "",
                    "Ком/кв.м": float(format(int(price_m2)/int(entity), ".2f")) if entity else "",
                    "Жителей": residence,
                    "Жителей в нп": int(settlement_population) if settlement_population else "", #entity_from_osm.get("residents") if entity_from_osm else "",
                    "Коммерческих объектов": entity or "",
                    "Прирост ст": "",
                    "Форма проведения": i['biddForm']['code'],
                    "Имущество": re.sub(r"^(.).+$", r"\1", bidd_type),
                    "Координаты": coord,
                    "Описание коммерческих объектов": f"""=HYPERLINK("{os.path.abspath("cache/objs_in_district")}/{info_object.get("lat")}_{info_object.get("lon")}.json", "{info_object.get("lat")}_{info_object.get("lon")}.json")""" \
                        if entity else "",
                    "Кадастровый номер": cadastral,  # characteristics['Кадастровый номер'],
                    "Этаж": floor,  # characteristics['Кадастровый номер'],
                    "Предсказываемая": "",
                    "Разница с реальной": "",
                    "Отдельный вход": entrance,
                    "Культурное наследие": legacy,
                    "Ремонт": "",

                }
                data["content"].append(object)

    with open(f"{folder}/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{folder}/result_full.json"