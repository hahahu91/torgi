import requests
import json

import random
from time import sleep, time
from bs4 import BeautifulSoup
import json
import csv

import os
import re
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
cookies = {
    '__utmz': '168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    '_ym_uid': '1662443318936557210',
    '_ym_d': '1662443318',
    'route': 'e8405c60164026df8ab71cd78b973f08',
    'JSESSIONID': 'TPkWnhNj0_7wYFU1HFLVlQgO63AYrxCGFgai4cTNKlnTYZ4Xof9T!-1874610497!-197974451',
    '__utma': '168694820.1016347800.1662443317.1662456597.1662531800.4',
    '__utmc': '168694820',
    '_ym_isad': '2',
    'wicket-modal-window-positions': 'multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C',
}

def get_archive_data(cookies):
    headers = {
        'Accept': 'text/xml',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; route=e8405c60164026df8ab71cd78b973f08; JSESSIONID=TPkWnhNj0_7wYFU1HFLVlQgO63AYrxCGFgai4cTNKlnTYZ4Xof9T!-1874610497!-197974451; __utma=168694820.1016347800.1662443317.1662456597.1662531800.4; __utmc=168694820; _ym_isad=2; wicket-modal-window-positions=multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C',
        'Origin': 'https://torgi.gov.ru',
        'Referer': 'https://torgi.gov.ru/lotSearch5.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Wicket-Ajax': 'true',
        'Wicket-FocusedElementId': 'id6f',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'id61_hf_0': '',
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

    print("get page 1")

    try:
        response = requests.post(
            f'https://torgi.gov.ru/lotSearch5.html?wicket:interface=:3:search_panel:buttonsPanel:search::IActivePageBehaviorListener:0:&wicket:ignoreIfNotActive=true&random={random.random()}',
        cookies=cookies, headers=headers, data=data, verify=False)
        src = response.text
        with open(f"../archive_data/index_1.html", "w", encoding="utf-8") as file:
            file.write(src)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        return True
    return False

def get_next_page(cookies, index):
    headers = {
        'Accept': 'text/xml',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; route=e8405c60164026df8ab71cd78b973f08; JSESSIONID=TPkWnhNj0_7wYFU1HFLVlQgO63AYrxCGFgai4cTNKlnTYZ4Xof9T!-1874610497!-197974451; __utma=168694820.1016347800.1662443317.1662456597.1662531800.4; __utmc=168694820; _ym_isad=2; wicket-modal-window-positions=multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C',
        'Referer': 'https://torgi.gov.ru/lotSearch5.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Wicket-Ajax': 'true',
        'Wicket-FocusedElementId': 'id8a',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        print(f"get page {index}")
        response = requests.get(
            f'https://torgi.gov.ru/lotSearch5.html?wicket:interface=:3:search_panel:resultTable:list:bottomToolbars:2:toolbar:span:navigator:next::IBehaviorListener:0:-1&random={random.random()}',
            cookies=cookies, headers=headers, verify=False)
        src = response.text
        if not src:
            return False
        with open(f"../archive_data/index_{index}.html", "w", encoding="utf-8") as file:
            file.write(src)
            return True
    except Exception as _ex:
        print(_ex)
        return False
def get_page_full_info_archive(url, id):
    cookies = {
        '__utmz': '168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        '_ym_uid': '1662443318936557210',
        '_ym_d': '1662443318',
        'wicket-modal-window-positions': 'multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C',
        'route': 'dd7990943a894a2adfdaab977c5d4630',
        'JSESSIONID': 's88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826',
        '__utma': '168694820.1016347800.1662443317.1662537194.1662615777.6',
        '__utmc': '168694820',
        '__utmt': '1',
        '_ym_isad': '2',
        '__utmb': '168694820.4.9.1662615849638',
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; wicket-modal-window-positions=multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C; route=dd7990943a894a2adfdaab977c5d4630; JSESSIONID=s88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826; __utma=168694820.1016347800.1662443317.1662537194.1662615777.6; __utmc=168694820; __utmt=1; _ym_isad=2; __utmb=168694820.4.9.1662615849638',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    session = requests.Session()
    response = session.get(
        f'https://torgi.gov.ru/{url}',
        headers=headers, verify=False)
    print(response.text)
    headers = {
        'Accept': 'text/xml',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; wicket-modal-window-positions=multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C; route=dd7990943a894a2adfdaab977c5d4630; JSESSIONID=s88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826; __utma=168694820.1016347800.1662443317.1662537194.1662615777.6; __utmc=168694820; __utmt=1; _ym_isad=2; __utmb=168694820.10.9.1662616172476',
        'Referer': f'{url}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Wicket-Ajax': 'true',
        'Wicket-FocusedElementId': 'idc2',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }


    cookies = {
        '__utmz': '168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        '_ym_uid': '1662443318936557210',
        '_ym_d': '1662443318',
        'wicket-modal-window-positions': 'multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C',
        'route': 'dd7990943a894a2adfdaab977c5d4630',
        'JSESSIONID': 's88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826',
        '__utma': '168694820.1016347800.1662443317.1662537194.1662615777.6',
        '__utmc': '168694820',
        '_ym_isad': '2',
        '__utmt': '1',
        '__utmb': '168694820.34.9.1662620645683',
    }

    headers = {
        'Accept': 'text/xml',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; wicket-modal-window-positions=multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C; route=dd7990943a894a2adfdaab977c5d4630; JSESSIONID=s88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826; __utma=168694820.1016347800.1662443317.1662537194.1662615777.6; __utmc=168694820; _ym_isad=2; __utmt=1; __utmb=168694820.34.9.1662620645683',
        'Pragma': 'no-cache',
        'Referer': 'https://torgi.gov.ru/restricted/notification/notificationView.html?notificationId=60240293&amp;lotId=60240559&amp;prevPageN=3',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Wicket-Ajax': 'true',
        'Wicket-FocusedElementId': 'id2a8',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response2 = session.get(
        'https://torgi.gov.ru/?wicket:interface=:20:notificationEditPanel:tabs:tabpanels-container:panels:1:panel:tableView:table:body:rows:1:cells:1:cell:view::IBehaviorListener:0:2&random=0.8321638061057477',
        cookies=cookies, headers=headers, verify=False)
    sleep(5)
    src = response2.text
    print(response)
    if not src:
        print(response)
        print(src)
        #return False
    else:
        print(src, "\n", "="*100,"\n", response2.content)
        if not os.path.exists('../archive_data/full_info'):
            os.makedirs('../archive_data/full_info')
        with open(f"../archive_data/full_info/{id}_2.html", "w", encoding="utf-8") as file:
            file.write(src)
    if not os.path.exists('../archive_data/full_info'):
        os.makedirs('../archive_data/full_info')
    with open(f"../archive_data/full_info/{id}.html", "w", encoding="utf-8") as file:
        file.write(response.text)
def test_get_data():
    cookies = {
        '__utmz': '168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        '_ym_uid': '1662443318936557210',
        '_ym_d': '1662443318',
        'wicket-modal-window-positions': 'multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C',
        'route': 'dd7990943a894a2adfdaab977c5d4630',
        'JSESSIONID': 's88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826',
        '__utma': '168694820.1016347800.1662443317.1662537194.1662615777.6',
        '__utmc': '168694820',
        '_ym_isad': '2',
        '__utmt': '1',
        '__utmb': '168694820.24.9.1662617874413',
    }

    headers = {
        'Accept': 'text/xml',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; wicket-modal-window-positions=multiSelectPopup%3A%3A410px%2C134px%2C850px%2C470px%7C; route=dd7990943a894a2adfdaab977c5d4630; JSESSIONID=s88bn2lDcoq7z65Majfnuqloa4No10v-30YlKCbTwxPgDfcB5V6p!-144684368!1030179826; __utma=168694820.1016347800.1662443317.1662537194.1662615777.6; __utmc=168694820; _ym_isad=2; __utmt=1; __utmb=168694820.24.9.1662617874413',
        'Referer': 'https://torgi.gov.ru/restricted/notification/notificationView.html?notificationId=60240293&amp;lotId=60240559&amp;prevPageN=3',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Wicket-Ajax': 'true',
        'Wicket-FocusedElementId': 'id1df',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        f'https://torgi.gov.ru/?wicket:interface=:13:notificationEditPanel:tabs:tabpanels-container:panels:1:panel:tableView:table:body:rows:1:cells:1:cell:view::IBehaviorListener:0:2&random={random.random()}',
        cookies=cookies, headers=headers, verify=False)
    src = response.text
    #print(response)
    with open(f"../archive_data/full_info/2.html", "w", encoding="utf-8") as file:
        file.write(src)

def get_all_pages_archive():
    if get_archive_data(cookies):
        sleep(random.randint(1,10))
        index = 2
        while get_next_page(cookies, index):
            index += 1

        print("exit")
        return index


def parse_object_from_archive_data(tr):
    cells = tr.find_all('td', class_="datacell")
    desc_page = cells[0].find_all("a")[1].get("href") if cells else ''
    download_page = cells[0].find_all("a")[2].get("href") if cells else ''
    num = re.sub('\W*лот\D+','_',cells[2].text.strip(), flags=re.IGNORECASE) if len(cells) > 1 else ''#.find_all("span")[1].text.strip() if len(cells) > 1 else ''

    desc = cells[3].text.strip() if len(cells) > 3 else ''
    price = int(re.sub("\D+",'', re.sub("[,\.]\d{2}\D",'',cells[4].text)).strip()) if len(cells) > 4 else ''
    type = cells[5].text.strip() if len(cells) > 5 else ''
    address = cells[6].text.strip() if len(cells) > 6 else ''
    return {
        "desc_page": desc_page,
        "download_page": download_page,
        "num": num,
        "desc": desc,
        "price": price,
        "type_auc": type,
        "address": address,
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


def get_desc_archive_obj(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': '__utmz=168694820.1662443317.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ym_uid=1662443318936557210; _ym_d=1662443318; __utma=168694820.1016347800.1662443317.1662537194.1662615777.6; wicket-modal-window-positions=multiSelectPopup%3A%3A248px%2C134px%2C850px%2C470px%7C',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    id = re.search(r"(id=.+$)",url, flags=re.IGNORECASE).group(0)
    response = requests.get(
        f'https://torgi.gov.ru/resources/org.apache.wicket.Application/printNotification?{id}&type=html', headers=headers, verify=False)

    with open(f"../archive_data/full_info/11.html", "w", encoding="utf-8") as file:
        file.write(response.text)

def get_desc_obj(path_to_file):
    if os.path.exists(path_to_file):
        with open(path_to_file, encoding="utf-8") as file:
            src = file.read()
            soup = BeautifulSoup(src, features="lxml")
            num_of_lot = re.search('_(\d+)\.\w+$', path_to_file).group(1)
            list = soup.find("b",text=re.compile(rf'Лот\D+{num_of_lot}', flags=re.IGNORECASE)).find_parent("table")
            date = soup.find(text=re.compile(r'Дата( и время)? проведения аукциона')).find_parent("tr").find_all("td")[1].text

            attribute = list.find_all('tr')
            obj = {}
            for lines in attribute:
                attrs = lines.find_all("td")
                if (len(attrs)) > 1:
                    if not attrs[1].find('td') and not attrs[0].find('td'):
                        obj[re.sub('^\W+|\W+$', '', attrs[0].text.strip())] = re.sub('^\W+|\W+$', '', attrs[1].text.strip())
            print(obj)
            obj["Дата проведения"] = date
            return obj

def main():
    #get_all_pages_archive()
    #get_page_full_info_archive('restricted/notification/notificationView.html?notificationId=60240293&amp;lotId=60240559&amp;prevPageN=3', 1)
    #get_desc_archive_obj('docview/notificationPrintPage.html?id=57839607&amp;prevPageN=3')
    get_desc_obj('../archive_data/full_info/11.html')
    #test_get_data()
if __name__ == '__main__':
    main()