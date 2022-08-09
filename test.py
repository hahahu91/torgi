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
from h3pandas_test import get_population_from_kontur_population, get_all_objs_from_kontur_population
from win32com import client
#data = pd.read_excel('torgi/output.xlsx', engine='openpyxl', index_col=0, sheet_name='Sheet1') #ensure_ascii=False,
from openpyxl import load_workbook
from openpyxl.styles import Font

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
        #coord = row[13].value
        address = row[7].value
        cadastr = row[9].value
        id = re.sub(r'^.+"([^"]+)"\)$', r'\1',row[3].value) if row[3].value else None
        #print(row[13].value)
        coord = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[13].value) if row[13].value else None
        #print(id, address, coord)
        if coord == None or coord == 'None, None':
            print(f"get info {index} in xls")
            info_object = get_info_object(id, address, cadastr)

            lat, lon = None, None
            if info_object:
                lat = info_object['lat']
                lon = info_object['lon']
                address = info_object['address']
                coord = f'''=HYPERLINK("https://yandex.ru/maps/?&text={lat}, {lon}", "{lat}, {lon}")''' if lat and lon and lat != "None" and lon != "None" else ""
                #print
                ws[f'N{index+1}'] = coord
                ws[f'H{index+1}'] = f'{address}'

                print(address, lat, lon)
        elif not os.path.exists(f'tmp/{id}.json'):
            save_address_with_geo(id, address, coord, cadastr)
    save_opening_output_file(file_xlsx_path)
    wb.save(file_xlsx_path)

def save_address_with_geo(id, address, coord, cadnum = None):
    try:
        lat, lon = coord.split(',')
    except Exception as _ex:
        print(_ex, coord)
    data_json = [{
        "value": f"{address}",
        "unrestricted_value": f"{address}",
        "data": {
            "country": "Россия",
            "country_iso_code": "RU",
            "geo_lat": f"{lat}",
            "geo_lon": f"{lon}",
            "qc_geo": "1",
            "flat_cadnum": f"{cadnum}" if cadnum else None
        }
    }]
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    with open(f'tmp/{id}.json', "w", encoding='utf8') as file:
        json.dump(data_json, file, ensure_ascii=False, indent=4)

def set_population_in_xlsx(file_xlsx_path):
    wb = load_workbook(file_xlsx_path)
    ws = wb['Sheet1']
    for index, row in enumerate(ws.rows):
        if (index == 0):
            continue
        # if (index == 2):
        #     break
        region = row[1].value
        coord = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[13].value).split(',')
        price_m2 = row[5].value
        #coord = row[13].value.split(',')
        #address = row[7].value
        #cadastr = row[9].value
        id = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[3].value)
        try:
            if coord[0] != "None" and coord[1] != "None":
                print(f"get objects in district {index} from xls")
                entity = get_commercial_assessment(float(coord[0]), float(coord[1]), region)
                if entity:
                    ws[f'O{index + 1}'] = f'{entity["residents"]}'
                    ws[f'P{index + 1}'] = f'{entity["entity"]}'
                    ws[f'Q{index + 1}'].font = Font( underline='single', color='0000FF')
                    ws[f'Q{index + 1}'] = f"""=HYPERLINK("{os.path.abspath("objs_in_district")}/{coord[0]}_{coord[1]}.json", "{coord[0]}_{coord[1]}.json")"""

                    ws[f'K{index + 1}'] = float(format(price_m2/int(entity["residents"]), ".2f")) if int(entity["residents"]) else ""
                    ws[f'K{index + 1}'].number_format = '_-* # ##0.00 ₽_-;-* # ##0.00 ₽_-'
                print(entity["residents"], entity["entity"])
        except Exception as _ex:
            raise
            print(_ex, coord)
    # currency_format = ws.add_format({'num_format': '# ### ##0 ₽'})
    # ws.set_column('K:K', 12, currency_format)
    #ws["K2"].number_format = '_-* # ##0,00 ₽_-;-* # ##0,00 ₽_-;_-* "-"?? ₽_-;_-@_-'
    # format_hyper = ws.add_format({'font_color': 'blue', 'underline': True})
    # ws.set_column('Q:Q', 22, format_hyper)
    #install_setting_of_columns(ws)
    save_opening_output_file(file_xlsx_path)
    wb.save(file_xlsx_path)

def set_population_from_h3_in_xlsx(file_xlsx_path):
    wb = load_workbook(file_xlsx_path)
    ws = wb['Sheet1']
    for index, row in enumerate(ws.rows):
        if (index == 0):
            continue
        # if (index == 2):
        #     break
        region = row[1].value
        coord = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[13].value).split(',')
        price_m2 = row[5].value
        id = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[3].value)
        try:
            if coord[0] != "None" and coord[1] != "None":
                print(f"get objects in district {index} from xls")
                population = get_population_from_kontur_population(float(coord[0]), float(coord[1]), region)
                if population:
                    ws[f'R{index + 1}'] = f'{population}'
                    ws[f'S{index + 1}'] = float(format(price_m2/int(population), ".2f")) if int(population) else ""
                    ws[f'S{index + 1}'].number_format = '_-* # ##0.00 ₽_-;-* # ##0.00 ₽_-'
                print(index, "\t", population)
        except Exception as _ex:
            raise
            print(_ex, coord)
    save_opening_output_file(file_xlsx_path)
    wb.save(file_xlsx_path)
def get_from_kontur_population(file_xlsx_path):
    wb = load_workbook(file_xlsx_path)
    ws = wb['Sheet1']
    objs = {}
    for index, row in enumerate(ws.rows):
        if (index == 0):
            continue
        try:
            coord = re.sub(r'^.+"([^"]+)"\)$', r'\1', row[13].value).split(',') if row[13].value else None
            if coord != None and coord[0] != "None" and coord[1] != "None":
                objs[index] = {"lat": coord[0], "lon": coord[1], "price_m2": row[5].value}

        except Exception as _ex:
            print(_ex, row[13].value, index)
            raise

    #print(objs)
    get_all_objs_from_kontur_population(objs)
    #print(objs)
    for index in objs:
        population = objs[index]["population"]
        ws[f'R{index + 1}'] = population
        ws[f'S{index + 1}'] = float(format(objs[index]["price_m2"] / int(population), ".2f")) if int(population) else ""
        ws[f'S{index + 1}'].number_format = '_-* # ##0.00 ₽_-;-* # ##0.00 ₽_-'
        #print(index, "\t", population)

    save_opening_output_file(file_xlsx_path)
    wb.save(file_xlsx_path)

#try_get_coords_again('torgi/output_archive.xlsx')
#set_population_in_xlsx('torgi/output_archive.xlsx')
get_from_kontur_population('torgi/output_archive.xlsx')


# Download and subset data
# df = pd.read_csv('https://github.com/uber-web/kepler.gl-data/raw/master/nyctrips/data.csv')
# df = df.rename({'pickup_longitude': 'lng', 'pickup_latitude': 'lat'}, axis=1)[['lng', 'lat', 'passenger_count']]
# qt = 0.1
# print(df.head())
# df = df.loc[(df['lng'] > df['lng'].quantile(qt)) & (df['lng'] < df['lng'].quantile(1-qt))
#             & (df['lat'] > df['lat'].quantile(qt)) & (df['lat'] < df['lat'].quantile(1-qt))]
# dfh3 = df.h3.geo_to_h3(10)
# print(dfh3.head())

