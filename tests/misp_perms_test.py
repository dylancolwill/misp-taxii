from functions import misp
import creds

url = "http://127.0.0.1:8000/taxii2/api1/collections/"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/taxii+json;version=2.1"
        }

data = None

try:
    data = misp.query_misp_api("/users/view/me", headers=headers)
except Exception as e:
    print("Error:", e)
    
print(data['Role']['perm_modify'])