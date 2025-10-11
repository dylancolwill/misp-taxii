import requests
import pprint
import creds


url = "http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/objects/report--59e9ec59-a888-48e4-afb4-441602de0b81"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/taxii+json;version=2.1"
        }
print("before header")
resp = requests.get(url, headers=headers)
# print(resp.status_code)

pprint.pp(resp)
print("before JSON call")
pprint.pp(resp.json())