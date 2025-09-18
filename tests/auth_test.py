from functions import misp
import creds

# incorrect auth
# auth="ABCDEF"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

try:
    data = misp.query_misp_api("/events", headers=headers)
except Exception as e:
    print("Error:", e)
    
# print(data)