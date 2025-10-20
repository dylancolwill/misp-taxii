import urllib3
# from pymisp import ExpandedPyMISP
import requests
from fastapi import Request, HTTPException, Depends
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# REMOVE BEFORE PRODUCTION
misp_ip='https://13.239.5.152'

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
    
    response = query_misp_api('/users/view/me', headers=headers)
    perm_modify = response['Role']['perm_modify']
    perm_add = response['Role']['perm_add']
    
    logger.debug(f'User perms - modify: {perm_modify}, add: {perm_add}')
    return perm_modify, perm_add

def get_headers(request: Request):
    api_key = request.headers.get('Authorization') 
    # print(f'GETHEADER{api_key}')
    # if not api_key:
    #     raise HTTPException(status_code=401, detail='Missing MISP API key')
    return dict(request.headers)

def headers_verify(headers):
    # check if header is passed
    if headers is None :
        logger.warning('Missing required headers')
        raise HTTPException(status_code=400, detail='Missing required header')
    
    if 'authorization' not in headers:
        logger.warning('Missing Authorization header')
        raise HTTPException(status_code=401, detail='The client needs to authenticate')
    if 'accept' not in headers:
        logger.warning('Missing Accept header')
        raise HTTPException(status_code=406, detail='Missing TAXII accept header')
    elif headers['accept'] != 'application/taxii+json;version=2.1':
        logger.warning('Invalid Accept header')
        raise HTTPException(status_code=406, detail='The media type provided in the Accept header is invalid')
    # logger.debug('Header verification complete')

def query_misp_api(endpoint: str, method: str = 'GET', data=None, headers=None):
    """
    function to call misp api dynamically
    allows other modules to query without duplicating logic
    """
    
    #set headers to lower case for consistency
    headers = {k.lower(): v for k, v in headers.items()}
    
    logger.info(f'Querying MISP API: {endpoint} with method {method}')
    
    # checks before processing
    headers_verify(headers=headers)
        
    # get api from header
    misp_api_key = headers.get('authorization')
    
    #set misp relevent headers
    misp_headers =  {'Authorization': misp_api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'}
    
    url = f'{misp_ip}{endpoint}'
    
    logger.debug(f'Making {method} request to MISP URL: {url}')
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=misp_headers, verify=False)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=misp_headers, verify=False, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=misp_headers, verify=False, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=misp_headers, verify=False)
        else:
            raise ValueError(f'unsupported http {method}')
        response.raise_for_status()
    except Exception as e:
        logger.error(f'Error querying MISP API: {e}')
        if e.response is not None and e.response.status_code == 403:
            raise HTTPException(status_code=403, detail='The client does not have access to this resource')
        else:
            raise HTTPException(status_code=400, detail='The server did not understand the request')

    # raise http errors
    
    # print('misp.py')
    # print(response)
    return response.json()
