import pytest
from bs4 import BeautifulSoup
from inc.get_archive import *

def setup_module(module):
    #init_something()
    pass

def teardown_module(module):
    #teardown_something()
    pass

def test_get_archive_data():
    test_data = get_objects_from_archive("test_data/index_1.html")
    assert len(test_data) == 10
    object1 = parse_object_from_archive_data(test_data[0])
    assert object1.get("desc_page") == "restricted/notification/notificationView.html?notificationId=60870189&lotId=60870363&prevPageN=2"
    assert object1.get("download_page") == "docview/notificationPrintPage.html?id=60870189&prevPageN=2"
    assert object1.get("num") == "150822/1353113/01_1"
    assert object1.get("desc") == "Продажа муниципального недвижимого имущества, находящегося в хозяйственном ведении МУП «Автоколонна № 1456» (нежилое помещение г. Череповец, пр. Победы, д. 195/25 пом.3)"
    assert object1.get("price") == 1900000
    assert object1.get("type_auc") == 'Аукцион'
    assert object1.get("address") == 'Вологодская обл, Череповец г, Победы пр-кт'

    object2 = parse_object_from_archive_data(test_data[1])
    assert object2.get("price") == 1001821

    object3 = parse_object_from_archive_data(test_data[6])
    print(object3)
    assert object3.get("price") == 59223

def test_get_archive_full_info():
    test_data = get_objects_from_archive("test_data/index_2.html")
    object1 = parse_object_from_archive_data(test_data[5])
    assert object1.get("price") == 1224000

def test_parsing_data_archive():
    assert get_desc_obj('test_data/full_info/11_1.html') == None






