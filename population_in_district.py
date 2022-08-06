#import pandas as pd
#import numpy as np
#import geopandas as gpd
#from matplotlib import pyplot as plt

import osmiter
import os
import re
#'lat': 56.6216708, 'lon': 47.8798082
def obj_in_districk(lat, lon, lat_obj, lon_obg):
    if not lat_obj or not lon_obg:
        return False
    if lat_obj >= float(lat)-0.0025 and lat_obj <= float(lat)+0.0025 and lon_obg >= float(lon)-0.005 and lon_obg <= float(lon)+0.005:
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

def count_commercial_assessment(feature_tags, entity):
    if "shop" in feature_tags:
        amount = 1 if not entity.get(feature_tags["shop"]) else entity.get(feature_tags["shop"]) + 1
        entity.update({feature_tags["shop"]: amount})
    elif feature_tags.get("building") and feature_tags["building"] in ["commercial", "service", "kindergarten", "school"]:
        amount = 1 if not entity.get(feature_tags["building"]) else entity.get(feature_tags["building"]) + 1
        entity.update({feature_tags["building"]: amount})
    elif feature_tags.get("amenity"):
        amount = 1 if not entity.get(feature_tags["amenity"]) else entity.get(feature_tags["amenity"]) + 1
        entity.update({feature_tags["amenity"]: amount})
    elif "leisure" in feature_tags:
        amount = 1 if not entity.get(feature_tags["leisure"]) else entity.get(feature_tags["leisure"]) + 1
        entity.update({feature_tags["leisure"]: amount})
    elif "bus" in feature_tags or "trolleybus" in feature_tags or "highway" in feature_tags and feature_tags["highway"] == "bus_stop":
        amount = 1 if not entity.get("bus_stop") else entity.get("bus_stop") + 1
        entity.update({"bus_stop": amount})
    elif "natural" not in feature_tags:
        residents = get_residents(feature_tags)
        amount = residents if not entity.get("residents") else entity.get("residents") + residents
        entity.update({"residents": amount})

def get_commercial_assessment(lat, lon, region):
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

#print(get_commercial_assessment(56.644718, 47.855835, 12))