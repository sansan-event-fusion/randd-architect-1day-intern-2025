import json

import requests

url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=1000"
response = requests.get(url, timeout=10)

data = json.loads(response.text)  # 文字列 → Pythonのリスト(dictのリスト)

# JSONファイルとして保存
with open("crads.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


