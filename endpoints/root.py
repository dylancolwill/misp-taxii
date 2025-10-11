# app/endpoints/api_root.py
from fastapi import APIRouter, HTTPException

router = APIRouter()

# static dictionary holding api root data 
# MAY NEED TO CHANGE TO BE DYNAMIC
api_roots_info = {
    'api1': {
        'title': 'Cosive',
        'description': 'Main CloudMISP connectivity',
        'versions': ['application/taxii+json;version=2.1'],
        'max_content_length': 104857600,  # 100mb
    }
}

def list_roots():
    
    """
    Returns list of usable api roots
    for discovery endpoint

    Returns:
        api_roots_info.keys(): ...
    """    
    return list(api_roots_info.keys())
    
@router.get('/taxii2/{api_root}/', tags=['API Root'])
async def get_api_root(api_root: str):
    
    """
    Return information about a specific api root

    Raises:
        404: If the API root does not exist in the dictionary

    Returns:
        api_roots_info: A dictionary containing API root data
    """    
    # check if api root exists in dict
    if api_root not in api_roots_info:
        raise HTTPException(status_code=404, detail='API Root not found')

    return api_roots_info[api_root]
