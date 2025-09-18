import requests

url = "http://127.0.0.1:8000/taxii2/api1/collections/"
auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

headers = {
            "Authorization": auth,
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/json"
        }

resp = requests.get(url, headers=headers)
# print(resp.status_code)
print(resp.json())
