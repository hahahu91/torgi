#import pandas as pd
#import numpy as np
#import geopandas as gpd
#from matplotlib import pyplot as plt

import osmiter
import os
import re
import json
import wget
import math
import datetime
from inc.population_from_h3 import distance
#'lat': 56.6216708, 'lon': 47.8798082

def obj_in_districk(x1, y1, x2, y2):
    if not x2 or not y2:
        return False
    return distance(x1, y1, x2, y2) < 0.0041

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
            levels = int(re.match(r"\d+", feature["building:levels"]).group(0))
            if levels == 1:
                return 3
            elif levels < 3: #Малоэтажное строение
                return levels * 5 * 3
            else:
                return levels * 10 * 3
        #не содержит записи о количестве этажей в здании
        if feature.get("building"):
            if feature["building"] in ["apartments", "residential"]:
                return 30*3
            if feature["building"] in ['house','yes']:
                return 3
    except Exception as _ex:
        print(_ex, "in", feature)
    return 0

def delete_if_older_30_days(path):
    timestamp = os.stat(path).st_ctime  # get timestamp of file
    createtime = datetime.datetime.fromtimestamp(timestamp)
    now = datetime.datetime.now()
    delta = now - createtime
    if delta.days > 30:
        os.remove(path)


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
        if amount:
            entity.update({"residents": amount})

def get_objs_in_district_from_cache(lat, lon):
    if os.path.exists(f'cache/objs_in_district/{lat}_{lon}.json'):
        with open(f'cache/objs_in_district/{lat}_{lon}.json', encoding='utf8') as f:
            entity = json.load(f)
            if entity:
                return count_entity(entity)
            else:
                delete_if_older_30_days(f'cache/objs_in_district/{lat}_{lon}.json')
    else:
        return {}

def count_entity(entity):
    entity_count = 0
    residents = 0
    if entity:
        residents = entity.get("residents")
        for category in entity:
            if category != "residents":
                entity_count += entity[category].get("count")

    return {
        'residents': residents,
        'entity': entity_count,
    }

def download_region_osm(region):
    url = f"https://needgeo.com/data/current/region/RU/{region}.pbf"
    print('Beginning file download with wget module')
    try:
        wget.download(url, f"konturs/{region}.pbf")
    except Exception as _ex:
        print(_ex, region, url)
        return None
    print('End file download with wget module')

def count_all_objs_in_region(objs, region):
    from config.regions_abbr import regions_abbr

    file_osm = regions_abbr.get(int(region)).get("abbr") if regions_abbr.get(int(region)) else None
    if not file_osm:
        print(f"not region {region} abbr")
        return None
    if not os.path.exists(f"konturs/{file_osm}.pbf"):
        print(f"not file_osm {region} region {file_osm}.pbf") #https://needgeo.com/data/current/region/RU/RU-ME.pbf
        download_region_osm(file_osm)

    print(f'proccesing region {region}: {file_osm}')
    print(objs)

    for feature in osmiter.iter_from_osm(f"konturs/{file_osm}.pbf", file_format="pbf"):
        for id_obj in objs:
            if obj_in_districk(float(id_obj['lat']), float(id_obj['lon']), feature.get('lat'), feature.get('lon')):
                id_obj["nodes"].add(feature['id'])
    #
            if feature["type"] == "way" and "building" in feature["tag"]:
                if feature.get("nd"):
                    for id in feature["nd"]:
                        if id in id_obj["nodes"]:
                            count_commercial_assessment(feature["tag"], id_obj["entity"])
                            break
            elif obj_in_districk(float(id_obj['lat']), float(id_obj['lon']), feature.get("lat"), feature.get("lon")):
                if feature["tag"] != {}:
                    count_commercial_assessment(feature["tag"], id_obj["entity"])
    #
    # return entity
    for id_obj in objs:
        del id_obj["nodes"]
        #if id_obj['entity']:
        if not os.path.exists('cache/objs_in_district'):
            os.makedirs('cache/objs_in_district')
        with open(f'cache/objs_in_district/{id_obj["lat"]}_{id_obj["lon"]}.json', "w", encoding='utf8') as file:
            json.dump(id_obj['entity'], file, ensure_ascii=False, indent=4)
        print(id_obj['entity'])

def get_data_population_from_osm_pseudo(lat, lon):
    data = {}
    for feature in osmiter.iter_from_osm(file_region_osm):
        if obj_in_districk(lat, lon, feature.get('lat'), feature.get('lon')):
            nodes.add(feature['id'])
        if feature["type"] == "way" and "building" in feature["tag"]:
            for id in feature["nd"]:
                if id in nodes:
                    count_commercial_assessment(feature["tag"], data)
                    break
        elif obj_in_districk(lat, lon, feature.get("lat"), feature.get("lon")):
            if feature["tag"] != {}:
                count_commercial_assessment(feature["tag"], data)
    return data

