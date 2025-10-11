from fastapi import APIRouter, Depends, HTTPException
from .root import list_roots

router = APIRouter()

# static discovery information
discovery_info= {
    'title': 'CloudMISP TAXII Server',
    'description': 'Integration with CloudMISP and TAXII protocol',
    # 'default': '/taxii2/api1/',  # api root endpoint
    'api_roots': [f'/taxii2/{key}/' for key in list_roots()] #dynamically build api roots defined in root endpoint
}

# MAY NEED TO AUTH BEFORE?
@router.get('/taxii2/', tags=['Discovery'])
async def get_discovery():
    """
    Provides metadata about the TAXII server

    Returns:
        discovery_info: A dictionary containing basic TAXII server metadata
    """    
    return discovery_info
