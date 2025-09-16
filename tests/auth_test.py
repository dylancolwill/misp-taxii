import functions.misp as misp

# incorrect auth
auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emd" 

headers = {
            "Authorization": auth,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

try:
    data = misp.query_misp_api("/events", headers=headers)
except Exception as e:
    print("Error:", e)