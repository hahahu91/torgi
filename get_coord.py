from setting import API_KEY, SECRET_KEY
from dadata import Dadata
import re
import os
import json
from population_from_h3 import distance
from get_address import reduce_addressing_elements

def get_info_object(id, address = "", cadastral = ""):
    info_object = None
    if os.path.exists(f'cache/tmp_loc/{id}.json'):
        #info_object
        with open(f'cache/tmp_loc/{id}.json', encoding='utf8') as f:
            info_object = json.load(f)

    if not info_object:
        print(f"get info {id}")
        info_object = get_location(address, cadastral)
        if info_object:
            if not os.path.exists('cache/tmp_loc'):
                os.makedirs('cache/tmp_loc')
            with open(f'cache/tmp_loc/{id}.json', "w", encoding='utf8') as file:
                json.dump(info_object, file, ensure_ascii=False, indent=4)

    if info_object:
        address = info_object[0]['value']
        lat = info_object[0]['data']['geo_lat']
        lon = info_object[0]['data']['geo_lon']
        postal_distance = info_object[0]['data'].get('postal_distance')
    else:
        lat, lon = None, None
        postal_distance = ""

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
                address = reduce_addressing_elements(address)
                result = dadata.suggest(name="address", query=address[:100], radius_meter=150)
            if result:
                if int(result[0]["data"]["qc_geo"]) <= 3:
                    result[0]["data"]["postal_distance"] = get_postal_distance(result[0]["data"]["geo_lat"], result[0]["data"]["geo_lon"])
                    return result

        except Exception as _ex:
            print(_ex, "except addr: ", address, "cad: ", cad_num)
    return None

def get_postal_distance(lat, lon):
    with Dadata(API_KEY, SECRET_KEY) as dadata:
    #print(address, API_KEY, SECRET_KEY)
        try:
            result = dadata.geolocate("postal_unit", lat=lat, lon=lon, radius_meters=3500)
            if result:
                return int(distance(float(lat), float(lon), float(result[0]["data"]["geo_lat"]), float(result[0]["data"]["geo_lon"]))* 1000)*100
            else:
                #print("not search")
                return 5000
        except Exception as _ex:
            print(_ex, result)
            raise
#print(int(float(get_postal_distance(55.834153, 37.356441))*100000))
if __name__ == "__main__":
    print(get_location("Тульская область, г.Тула, Привокзальный район, ул. М.Горького, д. 15а"))
