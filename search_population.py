import requests
import wikipedia
from bs4 import BeautifulSoup
def get_html_data():
    try:
        url = f"https://torgi.gov.ru/new/api/public/lotcards/search?subjRF=&biddType=&lotStatus=APPLICATIONS_SUBMISSION&catCode=11&withFacets=true&size=10"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "application/json, text/plain, */*",
        }
        count = 0

        # result = requests.get(url, headers=headers, verify=False).json();
        # time.sleep(5)
        wikipedia.set_lang("ru")
        result = wikipedia.search("""Российская Федерация, город intitle:Москва""")
        print(result)
        #print(wikipedia.page(result[0]).content)
        # with open("torgi/source-page.html", "w") as file:
        #     file.write(result[0])


    except Exception as _ex:
        print(_ex)


def main():

    get_html_data()
   # primary_processing("torgi/result_full.json")


if __name__ == "__main__":
    main()