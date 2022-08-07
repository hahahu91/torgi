import re
import json

def get_address(str):
    street_val = r"\s*\b(ул|проспек\w+|бульв|проезд|бульвар|аллея|пер|наб|шоссе|линия|просп|пр\Wкт|переулок|улиц\w+|пр)\b\.?"
    addr_val = r"\s*\b(г|д|р\.п|дер|пос|г\.о|сельское поселение|городской округ|населенный пункт|деревня|город|пгт|обл|респ|п|Респ\w+|республика|Республика\W+\w+|край|округ|область|район|р\Wо?н|с|ш|МО|ст\Wца|Федерация)\b\.?"
    addr_val_dig = r"\s*\b(пом|корпус|корп|зд|литера|кладовая|кв|д|к|дом|помещение|стр|строение)\b\.?"

    end_val = r"(,|(?<![дгрс])\.|$|площад\w+|общей|»|\(|;|с земельным) *"
    reg_exp = r'(:?по\b|:|\.|,|в\b)(?P<address>(:?' \
              r'(' \
              r'\s*\b(Россия|РФ)\b\.?|' \
              r'{addr_val}[^,:]+?|' \
              r'[^,:]+?({addr_val}|{street_val}))' \
              r'{end_val}|' \
              r'{addr_val_dig}( *№)?\s*[\di]+([\\/\- ]?\w{{,3}})?\s*{end_val}|' \
              r'{addr_val_dig}( *№)? *[\di]+\s*{addr_val_dig}\s*\w{{1,3}}(\W\w{{1,3}})?\s*{end_val}|' \
              r'{street_val}[^,:]+?(,\s*\d+[\\/ \d\w]{{,3}}\b\s*)?{end_val}' \
              r'){{2,}})' \
        .format(addr_val=addr_val, addr_val_dig=addr_val_dig, end_val=end_val, street_val=street_val)

    address_pattern = re.compile(reg_exp, flags=re.IGNORECASE)
    match = address_pattern.search(str)  # or address_pattern.search(i['lotName'])
    if match:
        address = re.sub(r'\s*((,|\.|площад\w+|»|\(|общей|с земельным) *)+$', '', match["address"])
        return address
    return ""
    # i['lotDescription'] = address_pattern.sub('', i['lotDescription'])
def test():
    count = 0
    for j in range(1, 11):

        with open(f"torgi/result/result_{j}.json", encoding='utf8') as f:
            json_data = json.load(f)

            for i in json_data['content']:

                print("1", i['lotDescription'])
                address = get_address(i['lotDescription'])
                if address:
                    print("2 good", address)
                else:
                    address = get_address(i['lotName'])
                    print("3", i['lotName'])
                    if address:
                        print("4 good", address)
                    if not address:
                        count += 1
                        print("5 bad", i['lotDescription'])
                #i['lotDescription'] = re.sub(re.escape(address), '', i['lotDescription'])
                print("\r\n")

    print(count)