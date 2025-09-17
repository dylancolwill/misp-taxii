from functions import misp

print('start')

auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

headers = {
            "Authorization": auth,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

data = None

print('querymisp')

try:
    data = misp.query_misp_api("/tags/index", headers=headers)
except Exception as e:
    print("Error:", e)
    
print('end')
print(data)