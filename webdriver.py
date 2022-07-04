from selenium import webdriver
from selenium.webdriver.firefox.options import Options as options
from selenium.webdriver.firefox.service import Service
import time
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import pickle

new_driver_path = r'D:\torgi_project\venv_torgi\geckodriver.exe'
new_binary_path = r'C:\Program Files\Mozilla Firefox\firefox.exe'



# url = "https://fedresurs.ru/search/bidding?searchString=%D0%BD%D0%B5%D0%B6%D0%B8%D0%BB%D0%BE%D0%B5%20%D0%BF%D0%BE%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D0%B5&limit=15&tradeType=%D0%92%D1%81%D0%B5&lots=%7B%22lotStartPrice%22:%2220%200000%22,%22lotFinishPrice%22:%221%20000%200000%22%7D&onlyAvailableToParticipate=true"

def get_source_html(url):

    options = webdriver.FirefoxOptions()
    useragent = UserAgent()
    options.set_preference("general.useragent.override", useragent.random)
    serv = Service(new_driver_path)
    driver = webdriver.Firefox(service=serv, options=options)

    driver.maximize_window()

    try:


        # for cookie in pickle.load(open(f"cookies", "rb")):
        #     driver.add_cookie(cookie)
        #driver.
        driver.post(url=url)
        time.sleep(50)
        #driver.refresh()
        #driver.post(r"https://old.bankrot.fedresurs.ru/Messages.aspx")

        # сохранение кук с настройками поиска
        pickle.dump(driver.get_cookies(), open("cookies", "wb"))


        driver.refresh()
        time.sleep(5)
        with open("torgi/source-page.html", "w") as file:
             file.write(driver.page_source)
        time.sleep(10)


        #while True:
            # find_more_element = driver.find_element_by_class_name("catalog-button-showMore")
            #
            # if driver.find_elements_by_class_name("hasmore-text"):
            #     with open("torgi/source-page.html", "w") as file:
            #         file.write(driver.page_source)
            #
            #     break
            # else:
            #     actions = ActionChains(driver)
            #     actions.move_to_element(find_more_element).perform()
            #     time.sleep(3)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


def main():
    get_source_html(
        url="https://old.bankrot.fedresurs.ru/Messages.aspx")
    # print(get_items_urls(file_path="file_path"))
    # print(get_data(file_path="file_path"))


if __name__ == "__main__":
    main()