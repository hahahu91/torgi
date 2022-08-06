# import pandas as pd
# import matplotlib.pyplot as plt
# import h3pandas
import re
import json
# from postal.expand import expand_address
# expand_address('Quatre vingt douze Ave des Champs-Élysées')

# Download and subset data
# df = pd.read_csv('https://github.com/uber-web/kepler.gl-data/raw/master/nyctrips/data.csv')
# df = df.rename({'pickup_longitude': 'lng', 'pickup_latitude': 'lat'}, axis=1)[['lng', 'lat', 'passenger_count']]
# qt = 0.1
# print(df.head())
# df = df.loc[(df['lng'] > df['lng'].quantile(qt)) & (df['lng'] < df['lng'].quantile(1-qt))
#             & (df['lat'] > df['lat'].quantile(qt)) & (df['lat'] < df['lat'].quantile(1-qt))]
# dfh3 = df.h3.geo_to_h3(10)
# print(dfh3.head())

def get_address(str):
    street_val = r"\s*\b(ул|проспек\w+|наб|улиц\w+|пр)\b\.?"
    addr_val = r"\s*\b(г|д|р\.п|дер|пос|г\.о|городской округ|населенный пункт|линия|деревня|город|шоссе|пгт|просп|обл|респ|п|Респ\w+|республика|Республика\W+\w+|край|округ|область|район|р\Wо?н|стр|с|ш|МО|ст\Wца|Федерация)\b\.?"
    addr_val_dig = r"\s*\b(пом|корпус|корп|кладовая|кв|д|дом|помещение)\b\.?"

    end_val = r"(,|(?<![дгрс])\.|$|площад\w+|») *"
    reg_exp = r'(?P<address>(:?помещение по|Нежилое помещение по|:|\.|,|в)(:?' \
              r'(' \
              r'\s*\b(Россия|РФ)\b\.?|' \
              r'{addr_val}[^,:]+|' \
              r'[^,:]+({addr_val}|{street_val}))' \
              r'{end_val}|' \
              r'{addr_val_dig}( *№)? *[\di]+([\\/ \d\w]{{,3}})\s*{end_val}|' \
              r'{street_val}[^,:]+(,\s*\d+[\\/ \d\w]{{,3}}\b\s*)?{end_val}' \
              r'){{2,}})' \
        .format(addr_val=addr_val, addr_val_dig=addr_val_dig, end_val=end_val, street_val=street_val)

    address_pattern = re.compile(reg_exp, flags=re.IGNORECASE)
    match = address_pattern.search(str)  # or address_pattern.search(i['lotName'])
    if match:
       return match["address"]
    return ""
    # i['lotDescription'] = address_pattern.sub('', i['lotDescription'])
def test():
    count = 0
    for j in range(1, 3):

        with open(f"torgi/archive/result_{j}.json", encoding='utf8') as f:
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
                i['lotDescription'] = re.sub(address, '', i['lotDescription'])
                print(i['lotDescription'])

    print(count)
test()
