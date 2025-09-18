# from functions import misp

# print('start')

# auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

# headers = {
#             "Authorization": auth,
#             "Accept": "application/json",
#             "Content-Type": "application/json"
#         }

# data = None

# print('querymisp')

# try:
#     data = misp.query_misp_api("/tags/index", headers=headers)
# except Exception as e:
#     print("Error:", e)
    
# print('end')
# print(data)


import requests
import creds

url = "http://127.0.0.1:8000/taxii2/api1/collections/"

headers = {
            "Authorization": creds.get_creds(),
            "Accept": "application/taxii+json;version=2.1",
            "Content-Type": "application/json"
        }

resp = requests.get(url, headers=headers)
# print(resp.status_code)
print(resp.json())
