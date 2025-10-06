import requests
import pprint
import creds


url = "http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/identity--7f4e0b2a-1f7b-41f4-9e76-a18fa1ce86e8"
auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

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