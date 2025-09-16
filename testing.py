import requests

url = "http://127.0.0.1:8000/taxii2/api1/collections/"
headers = {
    "Authorization": "w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K",
    "Accept": "application/taxii+json;version=2.1"
}

resp = requests.get(url, headers=headers)
print(resp.status_code)
print(resp.json())
