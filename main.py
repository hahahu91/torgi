import json
from datetime import datetime
import re
# from sklearn.linear_model import LinearRegression
# import matplotlib.pyplot as plt
import os

from get_data import get_data_from_torgi_gov, get_address_from_full_data
from population_in_district import get_objs_in_district_from_cache
from population_from_h3 import get_residents_from_cache_h3
from get_coord import get_location, get_info_object
from get_address import get_address, get_floor
from get_population import get_from_kontur_population, get_population_from_osm
from export_to_xlsx import export_to_xlsx


MIN_AREA = 10
BIDD_TYPE = {
    "229FZ":"Должников",
    "1041PP":"Государственное",
    "178FZ":"Муниципальное"
}
SUBJ_RF = {  12:'Mariy El',
            16:'Tatarstan',
            21:'Chuvashiya',
            43:'Kirovskaya',
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
        r'(,\s+)?(:?(с )?(кад\.|кадастро\w+|кн|к\/н|к\.н\.|cad)( ?\((или )?условный\))? ?(:?№|н\w+|ном\.|н\.)( об\w*\.?| помещ\w+)?|\():?\s*(?P<cad>(\d{2}\s*:\s*\d{2}\s*:\s*\d{4,8}\s*:\s*\d{1,5}[,;]?\s*)+)', flags=re.IGNORECASE)
    match = cad_pattern.search(obj['lotDescription']) or cad_pattern.search(obj['lotName'])

    cad = match["cad"] if match else None
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
        with open(f"{folder}/result_{j}.json", encoding='utf8') as f:
            json_data = json.load(f)
            count = 0
            for i in json_data['content'][:]:
                count += 1
                print(f"processing object {count}/{len(json_data['content'])} in file {j}/{amount_files}")
                characteristics = {}
                for characteristic in i['characteristics']:
                    characteristics[characteristic['name']] = characteristic[
                        'characteristicValue'] if "characteristicValue" in characteristic else None
                #получаем инфу про площадь
                area_pattern = re.compile(r'(,\s+)?(:?(общ(\w+)\s+)?площад\w+|общ\. ?пл\.)\D{1,20}(?P<area>[\d,.\s]+\d+)\s*(\(([^\d\W]+\s+)+[^\d\W]+\)\s*)?кв(\.|адратных)\s*м(:?\b|етров\b)', flags=re.IGNORECASE)
                match = area_pattern.search(i['lotDescription']) or area_pattern.search(i['lotName'])
                total_area = float(match['area'].replace(' ', '').replace(',', '.')) if match else characteristics.get('Общая площадь')
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

                floor = get_floor(i)
                bidd_type = BIDD_TYPE.get(i['biddType']['code']) or i['biddType']['code']

                cadastral = get_cadastral_num(i)
                if not cadastral:
                    cadastral = characteristics.get('Кадастровый номер')  or  characteristics.get(
                        'Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение') or None
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
                        print(info_object)

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
                    "Окончания подачи заявок": datetime.strptime(i['biddEndTime'], "%Y-%m-%dT%H:%M:%S.000+00:00").strftime("%d.%m.%y %H:%M"),
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
                    "Этаж": floor,  # characteristics['Кадастровый номер'],

                }
                data["content"].append(object)

    with open(f"{folder}/result_full.json", "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    return f"{folder}/result_full.json"




def main():
    #subjRF = (12:'Mariy El', 50:'MoscowOblast',92:'Sevastopol', 77:'Moscow', 21:'Chuvashiya', 58:'Penza', 91:'Krum') subj_rf="12,21,16,58,91,77,50"
    # biddType="229FZ":"Должников","1041PP":"обращенного в собственноcть государства","178FZ":"государсвенного и муниципального имущества"
    #lotStatus=SUCCEED сбор завершенных данных; status = "APPLICATIONS_SUBMISSION прием заявок
    subj_rf='1,2,3,5,10,11,12,13,14,16,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,41,42,43,44,45,46,47,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,66,68,69,70,71,72,73,74,76,79,86,89'
    amount_files = None
    status = "APPLICATIONS_SUBMISSION"
    folder = "cache/APPLICATIONS_SUBMISSION" if status != "SUCCEED" else "cache/SUCCEED"
    out_file = "torgi/output.xlsx" if status != "SUCCEED" else "torgi/output_archive.xlsx"
    #subj_rf = ','.join(map(str, SUBJ_RF.keys())) if status == 'APPLICATIONS_SUBMISSION' else ""
    bidd_type = '%s' % ",".join(BIDD_TYPE.keys())

    #amount_files = get_data_from_torgi_gov(bidd_type=bidd_type, subj_rf=subj_rf,  lot_status=status, out_folder=folder)
    path = transform_into_flatter_structure(amount_files=amount_files, folder=folder)
    export_to_xlsx(path, out_file)
    # get_from_kontur_population(out_file)
    # get_population_from_osm(out_file)


if __name__ == "__main__":
    main()