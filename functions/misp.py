import urllib3
from pymisp import ExpandedPyMISP
import requests
from fastapi import Request, HTTPException, Depends

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# REMOVE BEFORE PRODUCTION
auth="w35U4gMEzUl9TBox9kQcOQStIdAb4emdK1SoIY8K"

misp_ip="https://13.239.5.152"

# DONT NEED, AUTH IN EVERY REQUEST INSTEAD
# init
# misp = ExpandedPyMISP(misp_ip, auth)

# def connect():
#     """
#     return callable misp client to use in other modules
#     """
#     return misp

def get_headers(request: Request):
    api_key = request.headers.get("Authorization") 
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing MISP API key")
    return dict(request.headers)

def query_misp_api(endpoint: str, method: str = "GET", data=None, headers=None):
    """
    function to call misp api dynamically
    allows other modules to query without duplicating logic
    """

    # default headers
    # REMOVE BEFORE PRODUCTION
    if headers is None:
        headers = {
            "Authorization": auth,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
    # get api from header
    api_key = headers.get("Authorization")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing MISP API key")

    url = f"{misp_ip}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, verify=False, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, verify=False, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except Exception as e:
        raise RuntimeError(f"Error calling MISP {endpoint}: {e}")

    # raise http errors
    response.raise_for_status()

    return response.json()