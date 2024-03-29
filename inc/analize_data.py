import json
from datetime import datetime
import re
import pandas as pd
import numpy as np
import os

from inc.get_data import get_address_from_full_data
from inc.get_coord import get_location, get_info_object, get_locality_population
from inc.parse_data import *
from inc.population_in_district import get_residence
from setting import MIN_AREA,MAX_AREA, MAX_PRICE, MIN_PRICE, MIN_PRICE_ROOM_M2

def satisfy_parameters(obj, area, price, floor, type_object):
    if area < MIN_AREA or area > MAX_AREA:
        return False

    bad_words = re.compile(
        r'(:? дол[ия]\b|\bдолей\b|\bдолями\b|\bдолевой|\bдолевая|свинарник|(?<!не\W)\bжилое помещение\b)',
        flags=re.IGNORECASE)
    if bad_words.search(obj['lotDescription']) or bad_words.search(obj['lotName']):
        return False

    if price < MIN_PRICE or price > MAX_PRICE:
        return False

    price_m2 = price / area
    if price_m2 < MIN_PRICE_ROOM_M2:
        return False

    if (floor and int(floor) == -1):
        return False
    if re.search(r'(подвал|подпол|чердак|гараж)', type_object, flags=re.IGNORECASE):
        return False

    return True

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

                area = get_area(i)
                price = i.get('priceFin') or i.get('priceMin')
                price_m2 = price / area
                floor = get_floor_object(i)
                type_object = get_type_object(i)
                if not satisfy_parameters(obj= i, area=area, price=price, floor=floor, type_object=type_object):
                    continue

                land_plot = get_land_plot_object(i)
                entrance = get_entrance_object(i)
                repair = get_quality_repair_object(i)

                legacy = get_legacy_object(i)


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
                district  =  info_object.get('area')
                if settlement_type and settlement:
                    settlement_population = get_locality_population(df=df_population_in_locality, settlement=settlement, settlement_type=settlement_type,  area=district)

                object = {
                    "Регион": i['subjectRFCode'],
                    "Общая площадь": area,
                    "id": f"""=HYPERLINK("https://torgi.gov.ru/new/public/lots/lot/{i['id']}/(lotInfo:info)", "{i['id']}")""",
                    "Название": i['lotDescription'],
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d.%m.%y %H:%M"),
                    "Адрес": info_object.get("address") if info_object else address,
                    "Цена": price,
                    "Цена за кв.м": price_m2,
                    "Тип объекта": type_object,
                    "Чел/кв.м": float(format(int(price_m2)/int(residence), ".2f")) if residence else "",
                    "Ком/кв.м": float(format(int(price_m2)/int(entity), ".2f")) if entity else "",
                    "Жителей": residence,
                    "Жителей в нп": int(settlement_population) if settlement_population else "",
                    "Коммерческих объектов": entity or "",
                    "Прирост ст": "",
                    "Форма проведения": i['biddForm']['code'],
                    "Имущество": re.sub(r"^(.).+$", r"\1", bidd_type),
                    "Координаты": coord,
                    "Описание коммерческих объектов": f"""=HYPERLINK("{os.path.abspath("cache/objs_in_district")}/{info_object.get("lat")}_{info_object.get("lon")}.json", "{info_object.get("lat")}_{info_object.get("lon")}.json")""" \
                        if entity else "",
                    "Кадастровый номер": cadastral,
                    "Этаж": floor,
                    "Предсказываемая": "",
                    "Разница с реальной": "",
                    "Отдельный вход": entrance,
                    "Культурное наследие": legacy,
                    "Ремонт": repair,
                    "Земельный участок": land_plot,

                }
                data["content"].append(object)

    with open(f"{folder}/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{folder}/result_full.json"