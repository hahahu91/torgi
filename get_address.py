import re
import json
from address_test import TEST
from get_data import get_address_from_full_data

def get_address(str):
    street_val = r"\s*\b(ул|проспек\w+|ст|набережная|жилой район|бул|бульв|б-р|мкр|п\.г\.т|мкр\Wн|кв\Wл|квартал|проезд|бульвар|аллея|пер|наб|шоссе|линия|просп|пр\Wкт|переулок|улиц\w+|пр)\b\.?"
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
        address = re.sub(r'({end_val}$|^\s*{start_val}|^\s*{start_abs})*'.format(end_val=end_val, start_val=start_val, start_abs=start_abs), '', match["address"]).strip()
        return reduce_addressing_elements(address)
    return ""

def reduce_addressing_elements(address):
    from List_approved_abbr_addressing_elements import List_approved_abbr_addressing_elements as abbr_addr
    replacement_dict_regex = re.compile(r"\b(%s)\b" % "|".join(abbr_addr.keys()), flags=re.I)
    address = replacement_dict_regex.sub(lambda x: x.group().lower(), address)
    address = replacement_dict_regex.sub(lambda mo: abbr_addr.get(mo.group(1), mo.group(1)), address)

    return re.sub(r",[^,]+,\s*г\b", ", г", address)

def floor_to_num(str):
    minus1 = r'(подвал\w*|сарайка|подполь\w*|-1)'
    zero = r'(цокол\w+)'
    first = r'(1|перв\w+|i\b|земельны\w+)'
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


def get_floor(object):
    floor_val = r'[\s:#№\)]*\b(\d+|подвал\w*|сарайка|цокол\w+|перв\w+|втор\w+|трет\w+|надстроен\w+|подполь\w*|\d+-?\w{,2}|[ixv]+)\b\s*'
    reg_exp = r'(?P<floor>(:?' \
        r'этаж\w*{floor}|\bна{floor}этаж\w*|'\
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
def test():
    count = 0
    for j in range(1, 52):

        with open(f"cache/SUCCEED/result_{j}.json", encoding='utf8') as f:
            json_data = json.load(f)

            for i in json_data['content']:
                address = get_floor(i)
                if not address:

                    # address = get_floor(i['lotName'])
                    # if not address:
                    print("1", i['lotDescription'])
                    print("3", i['lotName'])
                    for char in i['characteristics']:
                        if char["name"] == "Расположение в пределах объекта недвижимости (этажа, части этажа, нескольких этажей)" and char.get("characteristicValue"):
                            print(char.get("characteristicValue"))

                    print("\r\n")
                   # print(i['characteristics'])
                    count += 1
                        #address = get_floor(i['id'])
                        #print(address)
                #print(address)

    # for t, str in TEST.items():
    #
    #     if get_address(t) != str:
    #         print(t)
    #         print(f"fail \"{str}\" != \"{get_address(t)}\"")


    print(count)
if __name__ == "__main__":
    test()
