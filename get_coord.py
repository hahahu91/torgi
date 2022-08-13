from setting import API_KEY, SECRET_KEY
from dadata import Dadata
import re
import os
import json

def get_info_object(id, address = "", cadastral = ""):
    print(os.path.abspath(f'cache/tmp_loc/{id}.json'))
    info_object = None
    if os.path.exists(f'cache/tmp_loc/{id}.json'):
        #info_object
        print("info")
        with open(f'cache/tmp_loc/{id}.json', encoding='utf8') as f:
            info_object = json.load(f)
            if address and info_object[0]['value'] != address:
                info_object = None
            print("get_info_obj", info_object)

    if not info_object:
        print("not info")
        info_object = get_location(address, cadastral)
        if info_object:
            if not os.path.exists('cache/tmp_loc'):
                os.makedirs('cache/tmp_loc')
            with open(f'cache/tmp_loc/{id}.json', "w", encoding='utf8') as file:
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

