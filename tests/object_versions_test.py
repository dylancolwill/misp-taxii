import requests
import creds

url = "http://127.0.0.1:8000/taxii2/api1/collections/d6ed313e-533a-55a6-aa06-4c00bc132812/objects/grouping--28f673f6-074f-484a-9a22-e89b786a5671/versions"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/taxii+json;version=2.1"
        }

resp = requests.get(url, headers=headers)
# print(resp.status_code)
print(resp.json())
