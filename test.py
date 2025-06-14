import json

import requests

with open("cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

cand_dict = {}

for card in cards:
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{card['user_id']}/similar_top10_users"
    response = requests.get(url)
    data = json.loads(response.text)

    cand_dict[card["full_name"]+'_'+card["company_name"]] = data

with open("cand.json", 'w') as f:
    json.dump(cand_dict, f, ensure_ascii=False, indent=4)


