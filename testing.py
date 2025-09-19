import requests
import pprint
url = "http://127.0.0.1:8000/taxii2/api1/collections/objects/"
auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

headers = {
            "Authorization": auth,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
print("before header")
resp = requests.post(url, headers=headers)
# print(resp.status_code)

pprint.pp(resp)
print("before JSOn call")
pprint.pp(resp)