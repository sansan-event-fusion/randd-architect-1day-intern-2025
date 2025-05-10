import requests

url = "https://circuit-trial.stg.rd.ds.sansan.com/api/health"
response = requests.get(url)

print(response.text)
