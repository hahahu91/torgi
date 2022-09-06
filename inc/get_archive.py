import requests
import json

import random
from time import sleep
from bs4 import BeautifulSoup
import json
import csv

import os
import re
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def get_archive_data():
    cookies = {
        'route': 'bacbee1088f260f29a437092a43725f1',
        '__utmc': '168694820',
        '__utmz': '168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        '_ym_uid': '1662443318936557210',
        '_ym_d': '1662443318',
        '_ym_isad': '2',
        'wicket-modal-window-positions': 'multiSelectPopup%3A%3A133px%2C134px%2C850px%2C470px%7C',
        'JSESSIONID': 'LFMSIoh_QJSfIGHDSReTtj54N40odeWLsQNiBdkijmb1OUhmN5op!1657466759!-518798756',
        '__utma': '168694820.1016347800.1662443317.1662451322.1662456597.3',
        '__utmt': '1',
        '__utmb': '168694820.10.9.1662456731978',
    }
    headers = {
        'Accept': 'text/xml',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'route=bacbee1088f260f29a437092a43725f1; __utmc=168694820; __utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; _ym_isad=2; wicket-modal-window-positions=multiSelectPopup%3A%3A133px%2C134px%2C850px%2C470px%7C; JSESSIONID=LFMSIoh_QJSfIGHDSReTtj54N40odeWLsQNiBdkijmb1OUhmN5op!1657466759!-518798756; __utma=168694820.1016347800.1662443317.1662451322.1662456597.3; __utmt=1; __utmb=168694820.10.9.1662456731978',
        'Origin': 'https://torgi.gov.ru',
        'Referer': 'https://torgi.gov.ru/lotSearch5.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Wicket-Ajax': 'true',
        'Wicket-FocusedElementId': 'id136',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    data = {
        'id128_hf_0': '',
        'extended:bidOrganization:bidOrganizationName': '',
        'extended:bidOrganization:bidOrganizationLocation': '',
        'extended:bidOrganization:bidOrganizationInn': '',
        'extended:bidOrganization:bidOrganizationKinds:multiSelectText': '',
        'extended:bidOrganization:bidOrganization': '',
        'extended:bidNumberExtended:bidNumber': '',
        'extended:bidNumberExtended:bidStatusId': '5',
        'extended:bidNumberExtended:detailComplaintType': '',
        'extended:bidNumberExtended:expireDateFrom': '',
        'extended:bidNumberExtended:expireDateTo': '',
        'extended:bidNumberExtended:publishDateFrom': '',
        'extended:bidNumberExtended:publishDateTo': '',
        'extended:bidNumberExtended:lastChangeDateFrom': '',
        'extended:bidNumberExtended:lastChangeDateTo': '',
        'extended:bidNumberExtended:resultDateFrom': '',
        'extended:bidNumberExtended:resultDateTo': '',
        'extended:propKind': '',
        'extended:propertyTypes:multiSelectText': 'Здание; Нежилое помещение; Предприятие; Строение',
        'extended:bidFormId': '',
        'extended:country': '',
        'extended:locationKladr': '',
        'extended:kladrIdStr': '',
        'extended:outputLists': '',
        'search_panel:buttonsPanel:search': '1',
    }

    response = requests.post('https://torgi.gov.ru/lotSearch5.html?wicket:interface=:5:search_panel:buttonsPanel:search::IActivePageBehaviorListener:0:&wicket:ignoreIfNotActive=true&random=0.6075842504193103', cookies=cookies, headers=headers, data=data)

    src = response.text
    #print(src)
    i = 1
    with open(f"index_{i}.html", "w", encoding="utf-8") as file:
        file.write(src)
        i += 1

def parse_object_from_archive_data(tr):
    cells = tr.find_all('td', class_="datacell")
    href = cells[0].find_all("a")[1].get("href")
    num = cells[2].find_all("span")[1].text.strip()
    desc = cells[3].text.strip()
    price = int(re.sub("\D+",'',cells[4].text.strip()))
    type = cells[5].text.strip()
    address = cells[6].text.strip()
    return {
        "href": href,
        "num": num,
        "desc": desc,
        "price": price,
        "type_auc": type,
        "address":address,
     }


def get_objects_from_archive(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src)

        list = soup.find("tbody").find_all('tr', {"class":"even datarow"})
        list += soup.find("tbody").find_all('tr', {"class":"odd datarow"})
        #print(list)
        return list