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

def get_user_perms(headers=None):
    """
    function to check if the user has writing perms
    required for some endpoints
    """
    
    response = query_misp_api("/users/view/me", headers=headers)
    perm_modify = response['Role']['perm_modify']
    
    return perm_modify

def get_headers(request: Request):
    api_key = request.headers.get("Authorization") 
    # print(f"GETHEADER{api_key}")
    # if not api_key:
    #     raise HTTPException(status_code=401, detail="Missing MISP API key")
    return dict(request.headers)

def headers_verify(headers):
    #set headers to lower case
    headers = {k.lower(): v for k, v in headers.items()}
    
    if headers is None :
        raise HTTPException(status_code=400, detail='Missing required header')
    if 'authorization' not in headers:
        raise HTTPException(status_code=401, detail='Missing authorization key in header')
    if 'accept' not in headers:
        raise HTTPException(status_code=400, detail='Missing TAXII accept header')
    elif headers["accept"] != "application/taxii+json;version=2.1":
        raise HTTPException(status_code=400, detail='Invalid accept header')
    print('header verification complete')
    

def query_misp_api(endpoint: str, method: str = "GET", data=None, headers=None):
    """
    function to call misp api dynamically
    allows other modules to query without duplicating logic
    """
        
    # get api from header
    misp_api_key = headers.get("authorization")
    
    misp_headers =  {"Authorization": misp_api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"}

    url = f"{misp_ip}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=misp_headers, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=misp_headers, verify=False, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=misp_headers, verify=False, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=misp_headers, verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except Exception as e:
        raise RuntimeError(f"Error calling MISP {endpoint}: {e}")

    # raise http errors
    response.raise_for_status()

    return response.json()
