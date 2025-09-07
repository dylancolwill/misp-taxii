import urllib3
from pymisp import PyMISP
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

misp_ip="https://13.239.5.152"

def connect():
    # using pymisp package, returns callable misp object
    misp = PyMISP(misp_ip, auth, False)
    return misp

def query_misp_api(endpoint): 
    # base for api get requests
    # takes api endpoint
    headers = {
        "Authorization": auth,
        "Accept": "application/json"
    }
    response = requests.get(f"{misp_ip}{endpoint}", headers=headers, verify=False)
    return response

def get_misp_events():
    # queries api for events, returns json
    # dont know how many events this returns
    events =query_misp_api("/events/index")
    return events.json()
    
# events = misp.search(limit=5)
# print(events)
