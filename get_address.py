import re
import json
from address_test import TEST


def get_address(str):
    street_val = r"\s*\b(ул|проспек\w+|ст|набережная|жилой район|бул|бульв|б-р|мкр|п\.г\.т|мкр\Wн|кв\Wл|квартал|проезд|бульвар|аллея|пер|наб|шоссе|линия|просп|пр\Wкт|переулок|улиц\w+|пр)\b\.?"
    addr_val = r"\s*\b(г|д|р\.п|дер|пос|г\.о|м\Wр\Wн|МО г\.п|городской|сельский|" \
               r"сельское поселение|село|городское поселение|поселок|городской округ|населенный пункт|" \
               r"деревня|город|пгт|обл|п|Респ\w*|край|округ|область|район|р\Wо?н|с|ш|МО|ст\Wца|Федерация)\b\.?"
    addr_val_dig = r"\s*\b(пом|корпус|корп|вл|зд|литера|кладовая|уч|кв|д|к|дом|помещение|стр|строение)\b\.?"

    end_val = r"(,|(?<![дгрс])\.|$|площад\w+|общей|»|\(|;|с земельным|и земельный|Кадастровый)+ *"
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

def test():



    count = 0
    for j in range(1, 51):

        with open(f"cache/SUCCEED/result_{j}.json", encoding='utf8') as f:
            json_data = json.load(f)

            for i in json_data['content']:

                print("1", i['lotDescription'])
                address = get_address(i['lotDescription'])
                if not address:
                    address = get_address(i['lotName'])
                    print("3", i['lotName'])
                    if not address:
                        count += 1
                        print("5 bad", i['lotDescription'])

                print(address)
                print("\r\n")
    for t, str in TEST.items():

        if get_address(t) != str:
            print(t)
            print(f"fail \"{str}\" != \"{get_address(t)}\"")


    print(count)