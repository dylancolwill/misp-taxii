import requests
import creds

url = "http://127.0.0.1:8000/taxii2/api1/collections/1883fdfb-249b-58f5-b445-87dff6eabc06/manifests"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/taxii+json;version=2.1"
        }

resp = requests.get(url, headers=headers)
# print(resp.status_code)
print(resp.json())
