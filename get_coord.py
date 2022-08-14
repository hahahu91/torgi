from setting import API_KEY, SECRET_KEY
from dadata import Dadata
import re
import os
import json
from h3pandas_test import distance
from get_address import reduce_addressing_elements

def get_info_object(id, address = "", cadastral = ""):
    print(os.path.abspath(f'cache/tmp_loc/{id}.json'))
    info_object = None
    if os.path.exists(f'cache/tmp_loc/{id}.json'):
        #info_object
        with open(f'cache/tmp_loc/{id}.json', encoding='utf8') as f:
            info_object = json.load(f)
            if address and info_object[0]['value'] != address:
                info_object = None
            print("get_info_obj", info_object)

    if not info_object:
        info_object = get_location(address, cadastral)
        if info_object:
            if not os.path.exists('cache/tmp_loc'):
                os.makedirs('cache/tmp_loc')
            with open(f'cache/tmp_loc/{id}.json', "w", encoding='utf8') as file:
                json.dump(info_object, file, ensure_ascii=False, indent=4)
    lat, lon = None, None
    postal_distance = 0
    if info_object:
        address = info_object[0]['value']
        lat = info_object[0]['data']['geo_lat']
        lon = info_object[0]['data']['geo_lon']
        postal_distance = info_object[0]['data']['postal_distance']

    return {
        'lat': lat,
        'lon': lon,
        'address': address,
        'postal_distance':postal_distance
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
                print(address)
                address = reduce_addressing_elements(address)

                print(address)
                result = dadata.suggest(name="address", query=address)
            if result:
                if int(result[0]["data"]["qc_geo"]) <= 3:
                    postal_distance = get_postal_distance(result[0]["data"]["geo_lat"], result[0]["data"]["geo_lon"])
                    if postal_distance:
                        result[0]["data"]["postal_distance"] = int(float(postal_distance) * 100000)
                        print(result[0]["data"]["postal_distance"])
                    return result

        except Exception as _ex:
            print(_ex, "except addr: ", address, "cad: ", cad_num)
    return None

def get_postal_distance(lat, lon):
    with Dadata(API_KEY, SECRET_KEY) as dadata:
    #print(address, API_KEY, SECRET_KEY)
        try:
            result = dadata.geolocate("postal_unit", lat=lat, lon=lon, radius_meters=4000)
            if result:
                return distance(float(lat), float(lon), float(result[0]["data"]["geo_lat"]), float(result[0]["data"]["geo_lon"]))

            else:
                #print("not search")
                return None
        except Exception as _ex:
            print(_ex, result)
            raise
#print(int(float(get_postal_distance(55.834153, 37.356441))*100000))
print(get_location("Московская область, Каширский район, г. Кашира, ул. Сергея Ионова, д. 3"))