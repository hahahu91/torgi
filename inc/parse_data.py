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


def get_address(str):
    street_val = r"\s*\b(ул|проспек\w+|ст|набережная|жилой район|бул|бульв|б-р|мкр|п\.г\.т|мкр\Wн|кв\Wл|" \
                 r"квартал|проезд|бульвар|аллея|микрорайон|пер|наб|шоссе|линия|просп|пр\Wкт|переулок|улиц\w+|пр)\b\.?"
    addr_val = r"\s*\b(г|д|р\.п|дер|пос|г\.о|м\Wр\Wн|МО г\.п|городской|сельский|" \
               r"сельское поселение|село|городское поселение|поселок|городской округ|населенный пункт|" \
               r"деревня|город|пгт|обл|п|Респ\w*|край|округ|область|район|р\Wо?н|с|ш|МО|ст\Wца|Федерация)\b\.?"
    addr_val_dig = r"\s*\b(корпус|корп|вл|зд|литера|кладовая|уч|д|к|дом|стр|строение)\b\.?"

    end_val = r"(,|(?<![дгрс])\.|$|площад\w+|общей|»|\(|;|с земельным|и земельный|Кадастровый|пом\b|помещение|кв\b|квартира|помещ\b)+ *"
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
        .format(addr_val=addr_val, addr_val_dig=addr_val_dig, end_val=end_val, street_val=street_val, start_val=start_val, start_abs=start_abs)
    # r'{addr_val}[^,:]+?({end_val}\w+,|' \
    address_pattern = re.compile(reg_exp, flags=re.IGNORECASE)
    match = address_pattern.search(str)
    if match:
        address = re.sub(r'({end_val}$|^\s*{start_val}|^\s*{start_abs}|[#№]\s*|(?<=\d)(,\s*\d+)+$|городской округ \w+,\s*(?=г))*'.format(end_val=end_val, start_val=start_val, start_abs=start_abs), '', match["address"]).strip()
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
        return '-1'
    elif re.search(zero, str, flags=re.IGNORECASE):
        return '0'
    elif re.search(first, str, flags=re.IGNORECASE):
        return '1'
    elif re.search(second, str, flags=re.IGNORECASE):
        return '2'
    elif re.search(third, str, flags=re.IGNORECASE):
        return '3'
    else:
        return '4'

def get_entrance(object): # отдельный вход (:>!\W+(:?отсусттвует|нет)))
    entrance = 0
    entrance_pattern = re.compile(r'(:?име\w+(\W+(\d+|один|два)\W*\w*)? вход\w*\W+(:?с торца дома|с закрыто\w+ двор\w+|со? сторон\w+)?|' \
                            r'(:?отдельн\w+(\W+и (:?\d+|один|два) совместн\w+)?\W+вход\w*|вход отдельный)(?!\W+(отс\w+|нет)))',
                            flags=re.IGNORECASE)
    #Вход в помещение только с дворовой
    if entrance_pattern.search(object['lotDescription']) or entrance_pattern.search(object['lotName']):
       return 1
    #вход в помещение через помещения
    not_entrance_r = re.compile(
        r'(Вход(:?\W+в помещение|\W+осуществляется)*\W*(:?через помещения|через подъезд|через места общего пользования|из( общего)? коридора|через жилое помещение|совместный)|'
        r'(:?отдельн\w+\W+вход\w*|вход отдельный)\W+(:?отсут\w+|нет))',
        flags=re.IGNORECASE)
    if entrance_pattern.search(object['lotDescription']) or entrance_pattern.search(object['lotName']):
        return -1
    return entrance

def get_type_object(object):
    type_pattern = re.compile(r'(:?(:?Комплек\w+ |Администра\w+ )*(?<!этаж[еa]\W)здани[йе]\W+(?!\d+\W+помещение)'
                              r'((:?тепло\w+ пункт\w+|УПК|бан\w+|подстанции|Штаб|казарм\w+|столов\w+|кафе|библиотек\w+|деревянн\w+|рабоч\w+ казар\w+|контор\w+ управлен\w+|учебно\W+производственного корпуса|(центрального )?теплового пункта|профилактория|бытов\w+ помещ\w*|детской молочной кухни)\W+)*|'
                              r'(:?Школ\w+|бытов\w+ помещен\w+|торгов\w+(\W+\w+)?|гаражн\w+\W*\w*|сарай|свинарник|производственное \w+|центр социальн\w+ обслуживан\w+ населен\w+|'
                              r'Проходн\w+|Растворо\W*бетонный узел|гараж\b|подвал|котельная|Ветеринарн\w+ пунк\w+|пилорам\w*|вальцев\w* мельниц\w*|овощехранил\w+|'
                              r'аптек\w+|cклад|бильярдн\w+|магази\w+|бокc\w*|офис\w*|Прачечн\w+|(столярн\w+ )?мастерск\w+|аптек\w+|молочн\w+ кухн\w+|'
                              r'помещение \w+(\W*\w*)? пункта|сарайка|Казарма))',
        flags=re.IGNORECASE)
    match = type_pattern.search(object["lotDescription"]) or type_pattern.search(object["lotName"])
    if not match:
        return "Нежилое помещение"

    return match[1]

def get_quality_repair(object):
    quality_repair_pattern = re.compile(r'(:?'
              r'(:?Комплек\w+ |Администра\w+ )*здани\w+\W+(?!\d+\W+помещение)(:?(:?тепло\w+ пункт\w+|УПК|бан\w+|подстанции|Штаб|казарм\w+|столов\w+|кафе|библиотек\w+|деревянн\w+|рабоч\w+ казар\w+|контор\w+ управлен\w+|учебно\W+производственного корпуса|(центрального )?теплового пункта|профилактория|бытов\w+ помещ\w*|детской молочной кухни)\W+)*|' \
              r'(:?Школ\w+|бытов\w+ помещен\w+|торгов\w+|гаражн\w+\W*\w*|сарай|свинарник|производственное \w+|центр социальн\w* обслуживан\w* населен\w*|'
              r'Проходн\w+|Растворо\W*бетонный узел|гараж\b|подвал|Котельн\w+|Ветеринарн\w+ пунк\w+|пилорам\w*|вальцев\w* мельниц\w*|овощехранил\w+|'
              r'аптек\w+|cклад|бильярдн\w+|дом\w+|магази\w+|бокc\w*|офис\w*|Прачечн\w+|(столярн\w+ )?мастерск\w+|аптек\w+|молочн\w+ кухн\w+|'
              r'помещение \w+(\W*\w*)* пункта|сарайка|Казарма))',
        flags=re.IGNORECASE)
    match = quality_repair.search(object["lotDescription"]) or quality_repair.search(object["lotName"])
    if not match:
        return "Нежилое помещение"
    return match[1]


def get_floor(object):
    floor_val = r'[\s:#№\)]*\b(\d+|подвал\w*|сарайка|цокол\w+|перв\w+|втор\w+|трет\w+|надстроен\w+|подполь\w*|\d+-?\w{,2}|[ixv]+)\b\s*'
    reg_exp = r'(?P<floor>(:?' \
        r'этаж\w*{floor}|этаж распол\w+{floor}|\bна{floor}этаж\w*|'\
        r'{floor}этаж\w*\b|\bв цокол\w+|подвал\w*|сарайка|в \w+илом \w+этажном (на \w+)?|'\
        r'\w+этажное \w+|на поэтажном плане ?-?{floor} этаж\w*|'\
        r'{floor}-?этажный|эт\.{floor}|номер на поэтажном плане{floor}|' \
        r'с земельным участком|земельный участок))'\
        .format(floor=floor_val)

    floor_pattern = re.compile(reg_exp, flags=re.IGNORECASE)
    floor = ""
    match = floor_pattern.search(object["lotDescription"]) or floor_pattern.search(object["lotName"])
    if not match:
        for char in object['characteristics']:
            if char["name"] == "Расположение в пределах объекта недвижимости (этажа, части этажа, нескольких этажей)" \
                    and char.get("characteristicValue"):
                #print(char.get("characteristicValue"))

                floor = char.get("characteristicValue")
    else:
        floor = match["floor"]
    if floor:
        floor_pattern = re.compile(r'(\d+|подвал\w*|сарайка|цокол\w+|перв\w+|втор\w+|трет\w+|надстроен\w+|подполь\w*|земельны\w+)', flags=re.IGNORECASE)
        match = floor_pattern.search(floor)
        if match:
            return floor_to_num(match[1])
    return ""

