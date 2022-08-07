# from rosreestr_api.clients import PKKRosreestrAPIClient
#
# api_client = PKKRosreestrAPIClient()
#
# # get building by cadastral id
# api_client.get_building_by_cadastral_id('16:50:110108:2815')
#
# # get parcel by cadastral id
# api_client.get_parcel_by_cadastral_id('77:17:0000000:11471')

# from rosreestr2coord import Area
#
# area = Area("58:12:1901007:308", center_only=True)
# # аргументы
# #   code='' - кадастровый номер участка
# #   area_type=1 - тип площади
# #   epsilon=5 - точность аппроксимации
# #   media_path='' - путь для временных файлов
# #   with_log=True - логирование
# #   coord_out='EPSG:4326' - или EPSG:3857 (будет удалена в последующих версиях)
# #   center_only=False - экспорт координат центров участка
# #   with_proxy=False - запросы через прокси
# #   use_cache=True - использовать кэширование запросов
# print(area.get_coord())

# import requests
# import time
#import random
from setting import API_KEY, SECRET_KEY
from dadata import Dadata
import re
import os
import json
#
# from urllib3.exceptions import InsecureRequestWarning
# # Suppress only the single warning from urllib3 needed.
# requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
#

# import json
def get_info_object(id, address = "", cadastral = ""):
    print(os.path.abspath(f'tmp/{id}.json'))
    if os.path.exists(f'tmp/{id}.json'):
        #info_object
        print("info")
        with open(f'tmp/{id}.json', encoding='utf8') as f:
            info_object = json.load(f)
            print("get_info_obj", info_object)
    else:
        print("not info")
        info_object = get_location(address, cadastral)
        if info_object:
            if not os.path.exists('tmp'):
                os.makedirs('tmp')
            with open(f'tmp/{id}.json', "w", encoding='utf8') as file:
                json.dump(info_object, file, ensure_ascii=False, indent=4)
    lat, lon = None, None
    if info_object:
        address = info_object[0]['value']
        lat = info_object[0]['data']['geo_lat']
        lon = info_object[0]['data']['geo_lon']

    return {
        'lat': lat,
        'lon': lon,
        'address': address
    }

def get_location(address = "", cad_num = ""):
    with Dadata(API_KEY, SECRET_KEY) as dadata:
        #print(address, API_KEY, SECRET_KEY)
        try:
            result = None
            if cad_num:
                for num in cad_num.split(","):
                    if num:
                        result = dadata.find_by_id("address", num)
                        if result:
                            break
            if not result and address:
                result = dadata.suggest(name="address", query=address)
            if result:
                if int(result[0]["data"]["qc_geo"]) <= 3:
                    return result

        except Exception as _ex:
            print(_ex, "except addr: ", address, "cad: ", cad_num)
    return None
# for i in ["21:12:000000:7595","12:05:0301005:413","58:05:0160203:870","16:05:010504:438","12:13:0990117:580","12:13:0990117:577","58:34:0010141:710","16:52:080201:142","21:01:030702:1810","21:01:030702:1809","21:01:030310:4184","21:01:030702:1806","21:02:000000:32513","21:02:000000:32517","21:01:010103:544","16:19:090301:75 ","58:12:1901007:308","16:01:110301:4410","58:29:3008002:4765","90:12:130101:188","21:11:290501:799","21:01:030310:2531","21:01:030310:2749","21:01:030310:2741","21:01:030310:2539","21:01:030310:2538","21:02:010510:988"]:
#print(get_location("г. Набережные Челны, ул. Профильная 59. (2230 (2)"))

#print(get_location("422230, РТ, г. Агрыз, ул. К. Маркса, д.74, расположенные по адресу РТ, г.Агрыз, ул.К.Маркса, д.74"))
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
#     "Accept": "application/json, text/plain, */*",
#     # "pragma": "no-cache",
#     # "referer": "https://pkk.rosreestr.ru/",
#     # "x-requested-with": "XMLHttpRequest",
# }
#     #url = f"https://pkk.rosreestr.ru/api/features/1/{cad}" #вечные ошибки
#     url = f"https://rosreestr.gov.ru/api/online/fir_object/{cad}"
#     try:
#         result = requests.get(url, headers=headers, verify=False).json();
#         if not result:
#             print("not get url")
#             continue
#         print(result)
#         if result.get('feature'):
#             print(result.get('feature').get("center") or "not")
#     except Exception as _ex:
#         print(_ex)
#
#     time.sleep(random.randint(15, 40))
# # with open(f"{folder}/result_{count}.json", "w", encoding='utf8') as file:
# #     json.dump(result, file, ensure_ascii=False, indent=4)
# #
