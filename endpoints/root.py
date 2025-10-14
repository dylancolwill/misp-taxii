# app/endpoints/api_root.py
from fastapi import APIRouter, HTTPException, Request
import functions.misp as misp

router = APIRouter()

# static dictionary holding api root data 
# MAY NEED TO CHANGE TO BE DYNAMIC
api_roots_info = {
    'api1': {
        'title': 'Cosive',
        'description': 'Main ClousMISP connectivity',
        'versions': ['application/taxii+json;version=2.1'],
        'max_content_length': 104857600,  # 100mb
    }
}

def list_roots():
    """
    returns list of usable api roots
    for discovery endpoint
    """
    return list(api_roots_info.keys())

def get_content_size(api_root: str) -> int:
    """
    returns the max content length for a given api root
    """
    if api_root in api_roots_info:
        return api_roots_info[api_root]['max_content_length']
    else:
        raise HTTPException(status_code=404, detail='API Root not found')
    
@router.get('/taxii2/{api_root}/', tags=['API Root'])
async def get_api_root(api_root: str, request:Request =None):
    """
    return information about a specific api root
    """
    # authenticate
    try:
        misp.get_user_perms(headers=dict(request.headers))
    except HTTPException as e:
        raise HTTPException(status_code=403, detail='The client does not have access to this resource')    
    
    # check if api root exists in dict
    if api_root not in api_roots_info:
        raise HTTPException(status_code=404, detail='The API Root is not found')

    return api_roots_info[api_root]
