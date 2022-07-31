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

def get_russia_gpkg():
    with open('Russia_boundary.json', 'r', encoding='utf8') as f:
        russia_boundary = gpd.GeoSeries.from_file(f).to_crs(epsg=3857) #EPSG:3857 3395
    russia = gpd.read_file("gzip://D:\\torgi_project\\kontur_population_20220630.gpkg.gz", mask=russia_boundary)

    russia.to_file("russia.gpkg", driver="GPKG")

def get_region_gpkg(region_name):
    with open(f'{region_name}_boundary.json', 'r', encoding='utf8') as f:
        boundary = gpd.GeoSeries.from_file(f).to_crs(epsg=3857)
    print("1\t", boundary.head())
    if not os.path.exists("russia.gpkg"):
        get_russia_gpkg()
    region = gpd.read_file("russia.gpkg", mask=boundary)

    region.to_file(f"{region_name}.gpkg", driver="GPKG")

def get_population_from_kontur_population(lat, lng, region):
    location = h3.geo_to_h3(lat, lng, 8)
    if (int(region) == 12):
        if not os.path.exists("mariel.gpkg"):
            get_region_gpkg("mariel")
        kontur = pd.DataFrame(gpd.read_file("mariyel.gpkg"))
    else:
        if not os.path.exists("russia.gpkg"):
            get_russia_gpkg()
        kontur = pd.DataFrame(gpd.read_file("russia.gpkg"))
    kontur.set_index("h3", inplace=True)

    return kontur.loc[(kontur.index == location)]["population"].get(0)

print(h3.hex_area(8)) #оршанка 56.916251, 47.882981
print("popul:\t", get_population_from_kontur_population(56.675958, 47.666557, 12))




#mariel_gpd = gpd.GeoDataFrame(mariel)
#mariel_gpd.plot(column='population', figsize=(8, 8))
#plt.show()
#print(russia_gdf.head())