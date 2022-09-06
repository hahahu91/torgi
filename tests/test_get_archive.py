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

    assert len(get_objects_from_archive("../inc/index_1.html")) == 10

    tr = BeautifulSoup('''<tr class="even datarow">
		<td class="datacell">
			<span>
				<div class="action-panel nowrap">
					<!--<br>-->
					<a href="#" title="Быстрый просмотр" id="id267" onclick="var wcall=wicketAjaxGet('?wicket:interface=:2:search_panel:resultTable:list:body:rows:91:cells:1:cell:quickView::IBehaviorListener:0:-1',function() { }.bind(this),function() { }.bind(this), function() {return Wicket.$('id267') != null;}.bind(this));return !wcall;"><img class="ss_sprite ss_zoom" src="img/s.gif" width="16px" height="16px"/><br/></a>
					<a href="restricted/notification/notificationView.html?notificationId=60870189&amp;lotId=60870363&amp;prevPageN=2" title="Просмотр"><img alt="Просмотр" title="Просмотр" class="ss_sprite ss_page_go" src="img/s.gif" width="16px" height="16px"/><br/></a>
					<a href="docview/notificationPrintPage.html?id=60870189&amp;prevPageN=2" title="Скачать"><img alt="Скачать" class="ss_sprite ss_printer" src="img/s.gif" width="16px" height="16px"/><br/></a>
				</div>
			</span>
		</td><td class="datacell left">
			<span>МУНИЦИПАЛЬНОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ &quot;ЧЕРЕПОВЕЦКАЯ АВТОКОЛОННА № 1456&quot;</span>
		</td><td class="datacell center">
			<span><span style="font-size:1em;">150822/1353113/01</span><br/><span class="span-black" style="font-size:1em;">Лот 1</span></span>
		</td><td class="datacell">
			<span>Продажа муниципального недвижимого имущества, находящегося в хозяйственном ведении МУП «Автоколонна № 1456» (нежилое помещение г. Череповец, пр. Победы, д. 195/25 пом.3)</span>
		</td><td class="datacell">
			<span>1 900 000 руб.</span>
		</td><td class="datacell">
			<span>Аукцион</span>
		</td><td class="datacell center">
			<span>Вологодская обл, Череповец г, Победы пр-кт</span>
		</td>
	</tr>''')
    object1 = parse_object_from_archive_data(tr)
    assert object1.get("href") == "restricted/notification/notificationView.html?notificationId=60870189&lotId=60870363&prevPageN=2"
    assert object1.get("num") == "150822/1353113/01"
    assert object1.get("desc") == "Продажа муниципального недвижимого имущества, находящегося в хозяйственном ведении МУП «Автоколонна № 1456» (нежилое помещение г. Череповец, пр. Победы, д. 195/25 пом.3)"
    assert object1.get("price") == 1900000
    assert object1.get("type_auc") == 'Аукцион'
    assert object1.get("address") == 'Вологодская обл, Череповец г, Победы пр-кт'









