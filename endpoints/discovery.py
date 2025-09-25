# app/endpoints/discovery.py
from fastapi import APIRouter, Depends, HTTPException
from .root import list_roots

router = APIRouter()

discovery_info= {
    'title': 'CloudMISP TAXII Server',
    'description': 'Integration with CloudMISP and TAXII protocol',
    # 'default': '/taxii2/api1/',  # api root endpoint
    'api_roots': [f'/taxii2/{key}/' for key in list_roots()]
}

# async def get_discovery(user=Depends(AUTHFUNC)):
# when figured out auth
@router.get('/taxii2/', tags=['Discovery'])
async def get_discovery():
    """
    returns list of api endpoints on server
    """
    return discovery_info
