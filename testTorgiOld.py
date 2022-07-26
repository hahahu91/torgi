import requests
import time
from urllib3.exceptions import InsecureRequestWarning
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

url="https://torgi.gov.ru/lotSearch2.html?bidKindId=8"
headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Accept": "application/json, text/plain, */*"
}

result = requests.get(url, headers=headers, verify=False)
time.sleep(5)

with open(f"result.html", "w", encoding='utf8') as file:
    file.write(result.text)