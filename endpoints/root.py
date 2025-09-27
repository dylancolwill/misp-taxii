# app/endpoints/api_root.py
from fastapi import APIRouter, HTTPException

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
    
@router.get('/taxii2/{api_root}/', tags=['API Root'])
async def get_api_root(api_root: str):
    """
    return information about a specific api root
    """
    # check if api root exists in dict
    if api_root not in api_roots_info:
        raise HTTPException(status_code=404, detail='API Root not found')

    return api_roots_info[api_root]
