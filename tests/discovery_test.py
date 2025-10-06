import requests
import creds

url = "http://127.0.0.1:8000/taxii2/"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/taxii+json;version=2.1"
        }

collectionResp = requests.get(url, headers=headers)
print(collectionResp)
# print(resp.status_code)
print(collectionResp.json())
