import urllib3
from pymisp import PyMISP
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth="61jDTaLYkKuPdNGc9DATaEa6DyM5N3Sf5CynNTl6"

def connect():
    # using pymisp package, returns callable misp object
    misp = PyMISP("https://localhost:8443", auth, False)
    return misp

def queryMispApi(url): 
    # base for api get requests
    # takes api endpoint
    headers = {
        "Authorization": auth,
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    return response

def getMispEventsApi():
    # queries api for events, returns json
    # dont know how many events this returns
    events =queryMispApi("https://localhost:8443/events/index")
    return events.json()
    
# events = misp.search(limit=5)
# print(events)
