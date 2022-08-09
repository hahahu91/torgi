#import pandas as pd
#import numpy as np
#import geopandas as gpd
#from matplotlib import pyplot as plt

import osmiter
import os
import re
import json
#'lat': 56.6216708, 'lon': 47.8798082
def obj_in_districk(lat, lon, lat_obj, lon_obg):
    if not lat_obj or not lon_obg:
        return False
    if float(lat_obj) >= float(lat)-0.0025 and float(lat_obj) <= float(lat)+0.0025 and float(lon_obg) >= float(lon)-0.005 and float(lon_obg) <= float(lon)+0.005:
        return True
    return False

def get_residents(feature):
    try:
        if feature.get("building"):
            if feature["building"] == "garage":
                return 1
            elif feature["building"] == "service":
                return 1
            elif feature["building"] == "construction":
                return 0
            elif feature["building"] == "kindergarten":
                return 10
        if feature.get("building:levels"):
            if int(re.match(r"\d+", feature["building:levels"]).group(0)) == 1:
                return 3
            elif int(re.match(r"\d+", feature["building:levels"]).group(0)) < 3: #Малоэтажное строение
                return int(feature["building:levels"]) * 5 * 3
            else:
                return int(re.match(r"\d+", feature["building:levels"]).group(0)) * 10 * 3
        #не содержит записи о количестве этажей в здании
        if feature.get("building"):
            if feature["building"] in ["apartments", "residential"]:
                return 30*3
            if feature["building"] in ['house','yes']:
                return 3
    except Exception as _ex:
        print(_ex, "in", feature)
    return 0

def count_tag(feature_tags, entity, tag):
    amount = entity.get(tag).get("count") + 1 if entity.get(tag) else 1
    list = entity.get(tag).get("detail") if entity.get(tag) else []
    list.append(feature_tags)
    entity.update({tag: {"count": amount, "detail": list}})

def count_commercial_assessment(feature_tags, entity):
    if "shop" in feature_tags:
        count_tag(feature_tags, entity, feature_tags["shop"])
    elif feature_tags.get("building") and feature_tags["building"] in ["commercial", "service", "kindergarten", "school"]:
        count_tag(feature_tags, entity, feature_tags["building"])
    elif feature_tags.get("amenity"):
        count_tag(feature_tags, entity, feature_tags["amenity"])
    elif "leisure" in feature_tags:
        count_tag(feature_tags, entity, feature_tags["leisure"])
    elif "bus" in feature_tags or "trolleybus" in feature_tags or "highway" in feature_tags and feature_tags["highway"] == "bus_stop":
        count_tag(feature_tags, entity, "bus_stop")
    elif "natural" not in feature_tags:
        residents = get_residents(feature_tags)
        amount = residents if not entity.get("residents") else entity.get("residents") + residents
        entity.update({"residents": amount})

def count_objects_in_district(lat, lon, region):
    from regions_abbr import regions_abbr
    file_osm = regions_abbr.get(int(region))["abbr"]
    if not file_osm:
        print(f"not region {region} abbr")
        return None
    if not os.path.exists(f"../konturs/{file_osm}.pbf"):
        print(f"not file_osm {region} region {file_osm}.pbf")
        return None
    nodes = set()
    entity = {}

    for feature in osmiter.iter_from_osm(f"../konturs/{file_osm}.pbf", file_format="pbf"):
        if obj_in_districk(lat, lon, feature.get("lat"), feature.get("lon")):
            nodes.add(feature["id"])
        if feature["type"]  == "way" and "building" in feature["tag"]:
            if feature.get("nd"):
                for id in feature["nd"]:
                    if id in nodes:
                        count_commercial_assessment(feature["tag"], entity)
                        break
        elif obj_in_districk(lat, lon, feature.get("lat"), feature.get("lon")):
            if feature["tag"] != {}:
                count_commercial_assessment(feature["tag"], entity)

    return entity

def get_commercial_assessment(lat, lon, region):
    if os.path.exists(f'objs_in_district/{lat}_{lon}.json'):
        # info_object
        print("get entity from file")
        with open(f'objs_in_district/{lat}_{lon}.json', encoding='utf8') as f:
            entity = json.load(f)
            print("entity", entity)
    else:
        print("not file in coords")
        entity = count_objects_in_district(lat, lon, region)
        if entity:
            if not os.path.exists('objs_in_district'):
                os.makedirs('objs_in_district')
            with open(f'objs_in_district/{lat}_{lon}.json', "w", encoding='utf8') as file:
                json.dump(entity, file, ensure_ascii=False, indent=4)
    entity_count = 0
    residents = 0
    if entity:
        residents = entity.get("residents")
        for category  in entity:
            if category != "residents":
                entity_count += entity[category].get("count")


    return {
        'residents': residents,
        'entity': entity_count,
    }


    #if entity != {}:
        #objs_in_district

#print(get_commercial_assessment(56.644718, 47.855835, 12))