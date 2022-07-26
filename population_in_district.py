import pandas as pd
import numpy as np
import geopandas as gpd
from matplotlib import pyplot as plt

# df = gpd.read_file("RU-ME.pbf")

import osmiter

shop_count = 0

#'lat': 56.6216708, 'lon': 47.8798082
def obj_in_districk(lat, lon, lat_obj, lon_obg):
    if not lat_obj or not lon_obg:
        return False
    if lat_obj >= lat-0.0025 and lat_obj <= lat+0.0025 and lon_obg >= lon-0.005 and lon_obg <= lon+0.005:
        return True
    return False
def get_residents(feature):
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
        if feature["building:levels"] == "1":
            return 3
        elif int(feature["building:levels"]) < 3: #Малоэтажное строение
            return int(feature["building:levels"]) * 5 * 3
        else:
            return int(feature["building:levels"]) * 10 * 3
    #не содержит записи о количестве этажей в здании
    if feature.get("building"):
        if feature["building"] in ["apartments", "residential"]:
            return 30*3
    return 0

#nodes = [705151256, 705151327, 705151181, 2761064854, 705151457, 705151256]
#nodes = [327582255, 1408477589, 2760900470, 1797449441, 1797449443, 1408477620, 2760900473, 1408477625, 1408477633, 1408477623, 1408477631, 1408477627, 1408477637, 1797449456, 1797449454, 1797449453, 1797449451, 1408477621, 1408477606, 1408477607, 1408477592, 1408477591, 1797449438, 327582280, 327582267, 1797449435, 1797449437, 1797449433, 1797449431, 705151055, 327582255]
nodes = []
count_residents = 0
# for el in [2761064827, 2761064767]:
#     if nodes.__contains__(el):
#         print("true")
#     else:
#         exit(1)
#
# for feature in osmiter.iter_from_osm("RU-ME.pbf", file_format="pbf"):
#     if obj_in_districk(56.644992, 47.855960, feature.get("lat"), feature.get("lon")) and feature["tag"] == {}:
#
#         #nodes.append(feature["id"])
#         print(feature)
# exit(1)
for feature in osmiter.iter_from_osm("RU-ME.pbf", file_format="pbf"):
   # if obj_in_districk(56.644992, 47.855960, feature.get("lat"), feature.get("lon")) and feature["tag"] != {} and "natural" not in feature["tag"]:
   #  if "building" in feature["tag"] and feature.get("tag").get("addr:street") == "Красноармейская улица" and feature.get("tag").get("addr:housenumber") == "111":
   #  if feature["id"] in nodes:
   #      print(feature)
    if obj_in_districk(56.644992, 47.855960, feature.get("lat"), feature.get("lon")) and feature["tag"] == {}:
        nodes.append(feature["id"])
    if feature["type"]  == "way" and "building" in feature["tag"]:
        if feature.get("nd"):
            for id in feature["nd"]:
                if id in nodes:
                     residents = get_residents(feature["tag"])
                     count_residents += residents
                     print(feature, residents)
                     break

    # if feature["type"] == "node" and "shop" in feature["tag"] and feature["id"] in nodes:
    #     shop_count += 1
    #     # if shop_count == 1:
    #     #    break

print(f"{count_residents} residents live in the area of this building")