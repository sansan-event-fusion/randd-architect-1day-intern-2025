import requests

res = requests.get(
    'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/9230809757',
    headers={'accept': 'application/json'}
)

print(res.status_code)
print(res.json())
print(res.headers)