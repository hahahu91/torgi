import requests
import wikipedia
from bs4 import BeautifulSoup
def get_population(addr):
    try:
        url = f"https://api.geotree.ru/address.php?key=C6TqmeUBcSXY&term={addr}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        }
        count = 0
        url=f"https://fias.nalog.ru/Search/Searching?text={addr}&division=1&filter[filters][0][value]={addr.lower()}&filter[filters][0][field]=PresentRow&filter[filters][0][operator]=contains&filter[filters][0][ignoreCase]=true&filter[logic]=and"

        req = requests.get(url, headers= headers)
        result = req.content.decode('utf-8')
        obj = {"content":result}
        print(obj['content'])
        # if req[0]["ObjectId"]:
        #     url=f'https://fias.nalog.ru/Search/SearchObjInfo?objId={req[0]["ObjectId"]}'
        #     req = requests.get(url, headers=headers)
        # result = requests.get(url, headers=headers, verify=False).json();
        # time.sleep(5)
       # wikipedia.set_lang("ru")
       # result = wikipedia.search("""Российская Федерация, город intitle:Москва""")
        #print(req.content)
        #print(wikipedia.page(result[0]).content)
        # with open("torgi/source-page.html", "w") as file:
        #     file.write(result[0])


    except Exception as _ex:
        print(_ex)


def main():

    get_population('Чебоксарский р-н, деревня Аркасы')
   # primary_processing("torgi/result_full.json")


if __name__ == "__main__":
    main()