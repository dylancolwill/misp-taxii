# app/endpoints/discovery.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

discovery_info= {
    "title": "CloudMISP TAXII Server",
    "description": "Integration with CloudMISP and TAXII protocol",
    # "default": "/taxii2/api1/",  # api root endpoint
    "api_roots": ["/taxii2/api1/"]
}

# async def get_discovery(user=Depends(AUTHFUNC)):
# when figured out auth
@router.get("/taxii2/", tags=["Discovery"])
async def get_discovery():
    """
    returns list of api endpoints on server
    """
    return discovery_info
