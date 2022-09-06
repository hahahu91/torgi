import re
import json
from inc.get_data import get_address_from_full_data
from config.List_approved_abbr_addressing_elements import List_approved_abbr_addressing_elements as abbr_addr

def get_address_pseudo(str):
    start_val = r'(:?\bпо(\s+адресу:?)\b|:|\.|\bв\b|\d,)'

    reg_exp = r'(?P<address>(:?{start_val}(' \
              r'{locality_val}[^,:;\(\)]+?{end_val}|' \
              r'[^,:;\(\)]+?({locality_val}|{street_val}){end_val})|' \
              r'((\w+\s*-\s*)?\w+, )?{street_val}[^,:;]+?(,\s*\d+[\\/ \d\w]{{,3}}\b\s*)?{end_val}' \
              r')+)' \
        .format(locality_val=locality_val, end_val=end_val, street_val=street_val,
                start_val=start_val)

    address_pattern = re.compile(reg_exp, flags=re.IGNORECASE)
    match = address_pattern.search(str)
    return normalize(match["address"])

def get_area(obj):
    total_area = ''
    for char in obj['characteristics']:
        if char["name"] == "Общая площадь" and char.get("characteristicValue"):
            total_area = float(str(char.get('characteristicValue')).replace(' ', '').replace(',', '.'))
    if not total_area:
        area_pattern = re.compile(
            r'(,\s+)?(:?(общ(\w+)\s+)?площад\w+|общ\. ?пл\.)\D{1,20}(?P<area>[\d,.\s]+\d+)\s*(\(([^\d\W]+\s+)+[^\d\W]+\)\s*)?кв(\.|адратных)\s*м(:?\b|етров\b)',
            flags=re.IGNORECASE)
        match = area_pattern.search(obj['lotDescription']) or area_pattern.search(obj['lotName'])
        total_area = float(match['area'].replace(' ', '').replace(',', '.')) if match else ''

    return total_area

def get_address(str):
    street_val = r"\s*\b(ул|проспек\w+|ст|набережная|жилой район|бул|бульв|б-р|мкр|п\.г\.т|мкр\Wн|кв\Wл|" \
                 r"квартал|проезд|бульвар|аллея|микрорайон|пер|наб|шоссе|линия|просп|пр\Wкт|переулок|улиц\w+|пр)\b\.?"
    addr_val = r"\s*\b(г|д|р\.п|дер|пос|г\.о|м\Wр\Wн|МО г\.п|городской|сельский|" \
               r"сельское поселение|село|городское поселение|поселок|городской округ|населенный пункт|" \
               r"деревня|город|пгт|обл|п|Респ\w*|край|округ|область|район|р\Wо?н|с|ш|МО|ст\Wца|Федерация)\b\.?"
    addr_val_dig = r"\s*\b(корпус|корп|вл|зд|литера|кладовая|уч|д|к|дом|стр|строение)\b\.?"
    end_val = r"(,|(?<![дгрс])\.|$|площад\w+|общей|»|\(|;|с земельным|и земельный|Кадастровый|пом\b|помещение|" \
              r"кв\b|квартира|помещ\b)+ *"
    start_val = r'(:?\bпо(\s+адресу:?)\b|:|\.|\bв\b|\d,)'
    start_abs = r'(:?местополож\w+\):|адрес\w*:|адрес\w*\s*-)'
    reg_exp =   r'(?P<address>(:?{start_val}(' \
                r'\s*\b(Россия|РФ|РМЭ|МО|РТ)\b|' \
                r'{addr_val}|' \
                r'[^,:;\(\)]+?({addr_val}){end_val})|' \
                r'{start_abs})' \
                r'[^:;]+(' \
                r'{addr_val_dig}( *№)?\s*[\dixv]+(([\\/\- ]|,?\s*{addr_val_dig}\s*)?\w{{,3}})?\s*{end_val}|' \
                r'{addr_val_dig}( *№)? *[\dixv]+\s*{addr_val_dig}\s*\w{{1,3}}(\W\w{{1,3}})?\s*{end_val}|' \
                r'((\w+\s*-\s*)?\w+, )?{street_val}[^,:;]+?(,\s*\d+[\\/ \d\w]{{,3}}\b\s*)?{end_val}' \
                r')+)' \
        .format(addr_val=addr_val, addr_val_dig=addr_val_dig, end_val=end_val,
                street_val=street_val, start_val=start_val, start_abs=start_abs)
    # r'{addr_val}[^,:]+?({end_val}\w+,|' \
    address_pattern = re.compile(reg_exp,flags=re.IGNORECASE)
    match = address_pattern.search(str)
    if match:
        address = re.sub(
                 r'({end_val}$|^\s*{start_val}|^\s*{start_abs}|[#№]\s*|(?<=\d)(,\s*\d+)+$|городской округ \w+,\s*(?=г))*'
                 .format(end_val=end_val, start_val=start_val, start_abs=start_abs), '', match["address"]).strip()
        return reduce_addressing_elements(address)
    return ""

def reduce_addressing_elements(address):
    replacement_dict_regex = re.compile(r"\b(%s)\b" % "|".join(abbr_addr.keys()), flags=re.I)
    address = replacement_dict_regex.sub(lambda x: x.group().lower(), address)
    address = replacement_dict_regex.sub(lambda mo: abbr_addr.get(mo.group(1), mo.group(1)), address)
    return re.sub(r",[^,]+,\s*г\b", ", г", address)

def parse_from_address_settlement(address):
    end_val = r"\s*(:?,|(?<![дгрс])\.|$|площад\w+|общей|»|\(|;|с земельным|и земельный|Кадастровый|пом\b|помещение|кв\b|" \
              r"квартира|помещ\b|ул|проспек\w+|ст|набережная|жилой район|бул|бульв|б-р|мкр|п\.г\.т|мкр\Wн|кв\Wл|" \
              r"квартал|проезд|бульвар|аллея|микрорайон|пер|наб|шоссе|линия|просп|пр\Wкт|переулок|улиц\w+|пр)"
    val = r"((?P<area>\w+(\s+мун\S+)?\s+р\S+н\b|\bр\S+н\b\s*(\w+)).+)?\b(?P<type>г|д|р\.п|дер|пос|г\.о|г\.п|сельский|" \
       r"сельское поселение|село|городское поселение|поселок|населенный пункт|" \
       r"деревня|город|пгт|п\.г\.т|п|[сc]|ш|ст\Wца)\b\W+(?P<city>[^,:;\(\)\d]+?){end_val}" \
        .format(end_val=end_val)
    address_pattern = re.compile(val, flags=re.IGNORECASE)
    match = address_pattern.search(address)

    if match:
        return match["city"], re.sub(r'((\w)\w*\W*)+', '\g<2>', match["type"]).strip(), re.sub(r'(\bр\S+н\b|\bмун\S+)', '', match["area"]).strip() if match["area"] else ""
    else:
        match = re.search(rf'^(?P<city>\w+)\W+{end_val}', address)
        if match:
            return match["city"], "г", ""
    return "", "", ""

def floor_to_num(str):
    minus1 = r'(подвал\w*|сарайка|подполь\w*|-1)'
    zero = r'(цокол\w+|полуподва\w+|подземный этаж)'
    first = r'(1|перв\w+|i\b|земельны\w+|надземный)'
    second = r'(2|втор\w+|ii\b)'
    third = r'(3|трет\w+|iii\b)'

    if re.search(minus1, str, flags=re.IGNORECASE):
        return -1
    elif re.search(zero, str, flags=re.IGNORECASE):
        return 0
    elif re.search(first, str, flags=re.IGNORECASE):
        return 1
    elif re.search(second, str, flags=re.IGNORECASE):
        return 2
    elif re.search(third, str, flags=re.IGNORECASE):
        return 3
    else:
        return 4

def get_entrance(str):
    if re.search(
        r'(:?име\w+(\W+(\d+|один|два)\W*\w*)? вход\w*\W+(:?с торца дома|с закрыто\w+ двор\w+|со? сторон\w+)?|' \
        r'(:?отдельн\w+(\W+и (:?\d+|один|два) совместн\w+)?\W+вход\w*|вход отдельный)(?!\W+(отс\w+|нет)))', str,
        flags=re.IGNORECASE):
        return 1
    if re.search(r'(Вход(:?\W+в помещени\w+|\W+осуществляется)*\W*(:?через помещения|через подъезд|через места общего пользования|из( общего)? коридора|через жилое помещение|совместный)|'
        r'(:?отдельн\w+\W+вход\w*|вход отдельный)\W+(:?отсут\w+|нет))', str,
        flags=re.IGNORECASE):
        return -1
    return None

def get_entrance_object(object): # отдельный вход (:>!\W+(:?отсусттвует|нет)))
    entrance = get_entrance(object['lotDescription']) or get_entrance(object['lotName'])
    if entrance:
       return entrance
    else:
        return ''

def get_land_plot(str):
    if re.search(r'(:?земел\w+\W+уч\w+)', str, flags=re.IGNORECASE):
        return 1
    return None

def get_land_plot_object(object):
    land_plot = get_land_plot(object['lotDescription']) or get_land_plot(object['lotName'])
    if land_plot:
        return land_plot
    else:
        return ''
def get_type(str):
    str = re.sub(r"(встроенные в \w+этажное( жилое)? здани\w+)", "", str)
    types = r'(:?' \
            r'Школ\w+|бытов\w+ помещен\w+|торгов\w+(\W+\w+)?|гаражн\w+\W*\w*|сарай|свинарник|производственное \w+|центр социальн\w+ обслуживан\w+ населен\w+|' \
            r'Проходн\w+|Растворо\W*бетонный узел|гараж\b|подвал|котельная|Ветеринарн\w+ пунк\w+|пилорам\w*|вальцев\w* мельниц\w*|овощехранил\w+|' \
            r'аптек\w+|cклад\w+|склад|спортивн\w+ зал\w*|бильярдн\w+|магази\w+|бокc\w*|офис\w*|Прачечн\w+|(столярн\w+ )?мастерск\w+|аптек\w+|молочн\w+ кухн\w+|' \
            r'помещение \w+(\W*\w*)? пункта|сарайка|машино\W*место|водозабор|Казарма|(\w+этажная )?автостоянка( с сервисным обслуживанием)?' \
            r')'
    type_pattern = re.compile(r'(:?(:?Комплек\w+ |Администра\w+ )*(?<!этаж[еa]\W)(\bжилое\W)?здани[йе]\W+(?!\d+\W+помещение)(назначение\W+нежилое\W+\w+\W+наименование\W+)?'
                              fr'((:?{types}|тепло\w+ пункт\w+|УПК|бан\w+|подстанции|Штаб|казарм\w+|столов\w+|кафе|библиотек\w+|деревянн\w+|рабоч\w+ казар\w+|контор\w+ управлен\w+|учебно\W+производственного корпуса|(центрального )?теплового пункта|профилактория|бытов\w+ помещ\w*|детской молочной кухни)\W+)*|'
                              fr'{types})',
                              flags=re.IGNORECASE)
    match = type_pattern.search(str)
    if match:
        type = re.sub(fr"^.*?({types}).*?$","\g<1>", match[1])
        return re.sub(r"^\W*(\w.+\w)\W*$","\g<1>", type)
    return None

def get_type_object(object):
    match = get_type(object["lotDescription"]) or get_type(object["lotName"])
    if match:
        return match
    return ''

def get_legacy(str):
    return re.search(r'(:?культурн\w+ наследи\w+)', str,
        flags=re.IGNORECASE)

def get_legacy_object(object):
    if get_legacy(object['lotDescription']) or get_legacy(object['lotName']):
        return 1
    else:
        for char in object['characteristics']:
            legacy = None
            if char["name"] == "Общие сведения об ограничениях и обременениях" and char.get("characteristicValue"):
                legacy = get_legacy(char.get("characteristicValue"))
            elif char["name"] == "Вид ограничений и обременений " and char.get("characteristicValue"):
                legacy = get_legacy(char.get("characteristicValue"))
            if legacy:
                return 1
    return ''


#                     'Общие сведения об ограничениях и обременениях
# является объектом культурного наследия республиканского значения '

def get_quality_repair(str):
    if re.search(r'(:?сделан \w+ ремонт|состояние хорошее|внутренняя отделка\W+простая)', str, flags=re.IGNORECASE):
        return 1
    elif re.search(r'(:?находится в удовлетворительном( техническом)? состоянии|состояние(\W+\w+)?\W+удовлетворительное|требуется косметический ремонт|состояние\W+стандартн\w+)', str, flags=re.IGNORECASE):
        return 0
    elif re.search(r'(:?состояние(\W+\w+)?\W+неудовлетворительное|находится в неудовлетворительном( техническом)? состоянии|находится в разрушенном состоянии|Объект незаверш\w+ строительства|Требуется ремонт|((:?крыша|пол|окна|двери|окна)(\W|и)+)+требуют ремонта)', str, flags=re.IGNORECASE):
        return -1
    elif re.search(r'(:?в плохом состоянии|в \w*разрушенном состоянии|(:?объект|помещение|здание) признан\w* аварийным|требуется капитальный ремонт)', str, flags=re.IGNORECASE):
        return -2
    else:
        match = re.search(r'износ\w*(\W+сост\wвляет)?\W+(\d+)[,\. ]*\d*%', str, flags=re.IGNORECASE)
        if match:
            if int(match[2]) <= 10:
                return 1
            elif int(match[2]) <= 30:
                return 0
            elif int(match[2]) <= 60:
                return -1
            else:
                return -2
    return None

def get_quality_repair_object(object):
    match = get_quality_repair(object["lotDescription"]) or get_quality_repair(object["lotName"])
    if match != None:
        return match
    return ""

def get_cadastral_num(obj):
    cad = ""
    cad_pattern = re.compile( #кадастровый (условный) номер
        r'(,\s+)?(:?(с )?(кад\.|кадастро\w+|кн|к\/н|к\.н\.|cad)( ?\((или )?условный\))? ?(:?№|н\w+|ном\.|н\.)( об\w*\.?| помещ\w+)?|\():?\s*(?P<cad>(\d{2}\s*:\s*\d{2}\s*:\s*\d{4,8}\s*:\s*\d{1,5}[,;]?\s*)+)', flags=re.IGNORECASE)
    match = cad_pattern.search(obj['lotDescription']) or cad_pattern.search(obj['lotName'])
    if match:
        cad = match["cad"]
    else:
        for char in obj['characteristics']:
            if char["name"] == "Кадастровый номер" and char.get("characteristicValue"):
                cad = char.get("characteristicValue")
            elif char["name"] == "Кадастровый номер объекта недвижимости (здания, сооружения), в пределах которого расположено помещение" and char.get("characteristicValue"):
                cad = char.get("characteristicValue")

    return cad

def get_floor(str): #этажа, на котором расположено помещение: 1
    floor_val = r'[\s:#№\)]*\b(\d+|подвал\w*|сарайка|цокол\w+|перв\w+|втор\w+|трет\w+|надстроен\w+|подполь\w*|\d+-?\w{,2}|[ixv]+)\b\s*'
    reg_exp = r'(?P<floor>(:?' \
              r'этаж\w*\W+(на\W+котором|где)\W+располо\w+\W+помещение{floor}|этаж\w*{floor}|этаж распол\w+{floor}|\bна{floor}этаж\w*|' \
              r'{floor}этаж\w*\b|\bв цокол\w+|подвал\w*|сарайка|в \w+илом \w+этажном (на \w+)?|' \
              r'\w+этажное \w+|на поэтажном плане ?-?{floor} этаж\w*|' \
              r'{floor}-?этажный|эт\.{floor}|номер на поэтажном плане{floor}|' \
              r'с земельным участком|земельный участок))' \
        .format(floor=floor_val)

    floor_pattern = re.compile(reg_exp, flags=re.IGNORECASE)
    floor = ""
    match = floor_pattern.search(str)
    if match:
        return match["floor"]
    return None

def get_floor_object(object):
    floor = get_floor(object["lotDescription"]) or get_floor(object["lotName"])
    if not floor:
        for char in object['characteristics']:
            if char["name"] == "Расположение в пределах объекта недвижимости (этажа, части этажа, нескольких этажей)" \
                    and char.get("characteristicValue"):
                #print(char.get("characteristicValue"))

                floor = char.get("characteristicValue")

    if floor:
        floor_pattern = re.compile(r'(\d+|подвал\w*|сарайка|цокол\w+|перв\w+|втор\w+|трет\w+|надстроен\w+|подпол\w*|\d+-?\w{,2}|[ixv]+|земельны\w+)', flags=re.IGNORECASE)
        match = floor_pattern.search(floor)
        if match:
            return floor_to_num(match[1])
    return ''

