from dadata import Dadata
import re
import os
import json
from config.dadata_setting import API_KEY, SECRET_KEY
from inc.population_from_h3 import distance
from inc.parse_data import reduce_addressing_elements, parse_from_address_settlement

def get_locality_population(df, settlement, settlement_type, area=""):

    if (settlement_type == "г"):
        settlement_population = df.loc[
            (df["municipality"].str.contains(rf'\b{settlement}\b', regex=True)) | ((df["settlement"] == settlement) & (
                    df["type"] == settlement_type))][
            "population"].sum()
    elif not area:
        settlement_population = df.loc[
            (df["settlement"] == settlement) & (
                    df["type"].str.contains(settlement_type, regex=False))]["population"].sum()
    elif area:
        settlement_population = df.loc[
            (df["settlement"] == settlement) & (
                df["municipality"].str.contains(rf'\b{area}\b', regex=True))][
            "population"].sum()

    return settlement_population or ""

def get_info_object(id, address = "", cadastral = "", cache_folder="cache/tmp_loc"):
    info_object = None
    if os.path.exists(f'{cache_folder}/{id}.json'):
        with open(f'{cache_folder}/{id}.json', encoding='utf8') as f:
            info_object = json.load(f)
    elif (address or cadastral):
        print(os.path.abspath(f'{cache_folder}/{id}.json'))
        print(f"get_info_object {id}")
        info_object = get_location(address, cadastral)
        if info_object:
            if not os.path.exists(f'{cache_folder}'):
                os.makedirs(f'{cache_folder}')
            with open(f'{cache_folder}/{id}.json', "w", encoding='utf8') as file:
                json.dump(info_object, file, ensure_ascii=False, indent=4)

    if info_object:
        #print(info_object)
        address = info_object[0]['value']
        lat = info_object[0]['data']['geo_lat']
        lon = info_object[0]['data']['geo_lon']
        if info_object[0]['data'].get('region_type') == "г":
            settlement_type = "г"
            settlement =  info_object[0]['data'].get('region')
            area = info_object[0]['data'].get('city_area') or info_object[0]['data'].get('city_district') or ""
        else:
            settlement_type = info_object[0]['data'].get('city_type') or info_object[0]['data'].get('settlement_type') or ""
            settlement = info_object[0]['data'].get('city') or info_object[0]['data'].get('settlement') or ""
            area = info_object[0]['data'].get('area') or ""
            #area = info_object[0]['data'].get('area') if info_object[0]['data'].get('settlement') and info_object[0]['data'].get('area') else ""
        if not settlement_type and not settlement:
            settlement, settlement_type, area = parse_from_address_settlement(address)
    else:
        settlement_type, settlement, area= "", "", ""
        lat, lon = None, None

    return {
        'lat': lat,
        'lon': lon,
        'address': address,
        'settlement_type': settlement_type,
        'settlement': settlement,
        'area': area,
    }

def get_location(address = "", cad_num = ""):
    with Dadata(API_KEY, SECRET_KEY) as dadata:
        #print(address, API_KEY, SECRET_KEY)
        try:
            result = None
            if address:
                address = reduce_addressing_elements(address)
                result = dadata.suggest(name="address", query=address[:100], radius_meter=150)
            if not result and cad_num:
                for num in cad_num.split(","):
                    if num:
                        result = dadata.find_by_id("address", num)
                        if result:
                            break
            if result:
                if int(result[0]["data"]["qc_geo"]) <= 3:
                    return result

        except Exception as _ex:
            print(_ex, "except addr: ", address, "cad: ", cad_num)
    return None

def main():
    import pandas as pd
    import numpy as np
    df_population_in_locality = pd.read_excel('../konturs/Population.xlsx',
                                              usecols=['municipality', 'settlement', 'type', 'population'])  # 'region',

    info = get_info_object("21000023940000000003_1", cache_folder="../cache/tmp_loc")
    print(info)
    area = info['area']
    settlement_type, settlement = info['settlement_type'], info['settlement']
    if settlement_type and settlement:
        settlement_population = get_locality_population(df=df_population_in_locality, settlement=settlement, settlement_type=settlement_type, area=area)
        print(settlement_population)
if __name__ == "__main__":
    main()
