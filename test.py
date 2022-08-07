# import pandas as pd
# import matplotlib.pyplot as plt
# import h3pandas
import re
import json
import numpy as np
import pandas as pd
import os
from get_coord import get_location, get_info_object
from population_in_district import get_commercial_assessment

from win32com import client
#data = pd.read_excel('torgi/output.xlsx', engine='openpyxl', index_col=0, sheet_name='Sheet1') #ensure_ascii=False,
from openpyxl import load_workbook


def save_opening_output_file(file_path):
    if os.path.exists(file_path):
        excelApp = client.Dispatch('Excel.Application')
        book = excelApp.Workbooks.open(os.path.abspath(file_path))
        excelApp.DisplayAlerts = False
        book.Save()
        book.Close()
#

def try_get_coords_again(file_xlsx_path):
    wb = load_workbook(file_xlsx_path)
    ws = wb['Sheet1']
    for index, row in enumerate(ws.rows):
        if (index == 0):
            continue
        coord = row[13].value
        address = row[7].value
        cadastr = row[9].value
        id = re.sub(r'^.+"([^"]+)"\)$', r'\1',row[3].value)
        #print(id, address, coord)
        if row[13].value == 'None, None' or row[13].value == None:

            info_object = get_info_object(id, address, cadastr)
            lat, lon = None, None
            if info_object:
                lat = info_object['lat']
                lon = info_object['lon']
                address = info_object['address']
                #print
                ws[f'N{index+1}'] = f'{lat}, {lon}'
                ws[f'H{index+1}'] = f'{address}'

                print(address, lat, lon)
    save_opening_output_file(file_xlsx_path)
    wb.save(file_xlsx_path)


def set_population_in_xlsx(file_xlsx_path):
    wb = load_workbook(file_xlsx_path)
    ws = wb['Sheet1']
    for index, row in enumerate(ws.rows):
        if (index == 0):
            continue
        if (index == 2):
            break
        region = row[1].value
        coord = row[13].value.split(',')
        #address = row[7].value
        #cadastr = row[9].value
        id = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[3].value)
        print("count in ", region, coord)
        try:
            if coord[0] != "None" and coord[1] != "None":
                entity = get_commercial_assessment(coord[0], coord[1], region)
                if entity:
                    ws[f'O{index+1}'] = f'{entity["residents"]}'
                    ws[f'P{index+1}'] = f'{entity["entity"]}'
                    ws[f'Q{index+1}'] = f"""=HYPERLINK("{os.path.abspath("objs_in_district")}/{coord[0]}_{coord[1]}.json", "{coord[0]}_{coord[1]}.json")"""

                print(region, coord)
        except Exception as _ex:
            print(_ex, coord)
    save_opening_output_file(file_xlsx_path)
    wb.save(file_xlsx_path)

    # if lat and lon and i.get('subjectRFCode'):
    #     try:
    #         commercial_assessment = get_commercial_assessment(lat, lon, i['subjectRFCode'])
    #     except Exception as _ex:
    #         print(_ex, "\r\n", lat, lon, i['subjectRFCode'])
    # residents = 0
    # shops = 0
    # if commercial_assessment:
    #     residents = commercial_assessment.get("residents")
    #     for category  in commercial_assessment:
    #         if category != "residents":
    #             shops += commercial_assessment.get(category)


#try_get_coords_again('torgi/output_archive.xlsx')
set_population_in_xlsx('torgi/output.xlsx')

#print(type(ws))
# data = pd.DataFrame(ws.values)
#
# wb.save('torgi/output2.xlsx')
# with pd.ExcelWriter('torgi/output3.xlsx', engine='xlsxwriter', mode="w") as writer:
#     data.to_excel(writer, encoding='utf-8')
    #install_setting_of_columns(writer)

# for ob in data:
#     print(ob)
# from postal.expand import expand_address
# expand_address('Quatre vingt douze Ave des Champs-Élysées')

# Download and subset data
# df = pd.read_csv('https://github.com/uber-web/kepler.gl-data/raw/master/nyctrips/data.csv')
# df = df.rename({'pickup_longitude': 'lng', 'pickup_latitude': 'lat'}, axis=1)[['lng', 'lat', 'passenger_count']]
# qt = 0.1
# print(df.head())
# df = df.loc[(df['lng'] > df['lng'].quantile(qt)) & (df['lng'] < df['lng'].quantile(1-qt))
#             & (df['lat'] > df['lat'].quantile(qt)) & (df['lat'] < df['lat'].quantile(1-qt))]
# dfh3 = df.h3.geo_to_h3(10)
# print(dfh3.head())

