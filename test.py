# import pandas as pd
# import matplotlib.pyplot as plt
# import h3pandas
import re
import json
import numpy as np
import pandas as pd
import os
from get_coord import get_location, get_info_object

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
# if os.path.exists(f'tmp/21000005000000003050_1.json'):
#     #info_object
#     print("info")
# else:
#     print("not info")
#
#
wb = load_workbook('torgi/output.xlsx')
ws = wb['Sheet1']
count = 0
for row in ws.rows:
    count += 1
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
            ws[f'N{count}'] = f'{lat}, {lon}'
            ws[f'H{count}'] = f'{address}'

            print(address, lat, lon)
save_opening_output_file('torgi/output.xlsx')
wb.save('torgi/output.xlsx')
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

