# app/endpoints/discovery.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

# Dummy discovery data
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
    TAXII 2.1 Discovery Endpoint
    ---
    Returns a list of API roots available on this server.
    First endpoint client calls to discover the server.
    """
    return discovery_info