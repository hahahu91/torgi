import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import h3pandas
import h3
#33
import gzip
import json

import matplotlib.pyplot as plt
import os
import numpy
import math

def get_russia_gpkg():
    with open('Russia_boundary.json', 'r', encoding='utf8') as f:
        russia_boundary = gpd.GeoSeries.from_file(f).to_crs(epsg=3857) #EPSG:3857 3395
    russia = gpd.read_file("gzip://../konturs/kontur_population_20220630.gpkg.gz", mask=russia_boundary)

    russia.to_file("../konturs/russia.gpkg", driver="GPKG")

def get_region_gpkg(region_name):
    with open(f'{region_name}_boundary.json', 'r', encoding='utf8') as f:
        boundary = gpd.GeoSeries.from_file(f).to_crs(epsg=3857)
    print("1\t", boundary.head())
    if not os.path.exists("../konturs/russia.gpkg"):
        get_russia_gpkg()
    region = gpd.read_file("../konturs/russia.gpkg", mask=boundary)

    region.to_file(f"{region_name}.gpkg", driver="GPKG")

def get_population_from_kontur_population(lat, lng, region):
    location = h3.geo_to_h3(lat, lng, 8)
    if (int(region) == 12):
        if not os.path.exists("../konturs/mariel.gpkg"):
            get_region_gpkg("mariel")
        kontur = pd.DataFrame(gpd.read_file("../konturs/mariel.gpkg"))
    else:
        if not os.path.exists("../konturs/russia.gpkg"):
            get_russia_gpkg()
        kontur = pd.DataFrame(gpd.read_file("../konturs/russia.gpkg"))
    kontur.set_index("h3", inplace=True)

    return kontur.loc[(kontur.index == location)]["population"].get(0)

def get_all_objs_from_kontur_population(objs):
    if not os.path.exists("../konturs/russia.gpkg"):
        get_russia_gpkg()
    kontur = pd.DataFrame(gpd.read_file("../konturs/russia.gpkg"))
    kontur.set_index("h3", inplace=True)
    #answer = []
    for index in objs:

        h3_data = get_nearest_neighbor(float(objs[index]["lat"]), float(objs[index]["lon"]))
        population = 0
        for obj in h3_data:
            population += kontur.loc[(kontur.index == obj)]["population"].get(0) or 0
        objs[index]["population"] = int(population/len(h3_data))
        if objs[index]["population"]:
            if not os.path.exists('cache/population_in_h3'):
                os.makedirs('cache/population_in_h3')
            with open(f'cache/population_in_h3/{objs[index]["lat"]}_{objs[index]["lon"]}.json', "w", encoding='utf8') as file:
                json.dump(objs[index], file, ensure_ascii=False, indent=4)

        print(index, "/", len(objs), ":\t", int(population / len(h3_data)))


    return

def distance(x1, y1, x2, y2):
    return math.sqrt((float(x1)-float(x2))**2+(float(y2)-float(y1))**2)

def get_nearest_neighbor(lat, lon):
    p = h3.geo_to_h3(lat, lon, 8)
    geo_boundary = h3.h3_to_geo_boundary(p)
    ring_poly = h3.k_ring(p, 1)
    nearest_points = []
    for point in geo_boundary:
        if distance(point[0], point[1], lat, lon) < 0.00325:
            nearest_points = (point[0], point[1])
    nearest_poly = []
    for poly in ring_poly:
        loc = h3.h3_to_geo_boundary(poly)
        if nearest_points in loc:
            nearest_poly.append(poly)
    if not nearest_points:
        return [p]
    else:
        return nearest_poly

