from fastapi import APIRouter, Depends, HTTPException, Request
from .root import list_root_keys
import functions.misp as misp

router = APIRouter()

# static discovery information
discovery_info= {
    'title': 'CloudMISP TAXII Server',
    'description': 'Integration with CloudMISP and TAXII protocol',
    # 'default': '/taxii2/api1/',  # api root endpoint
    'api_roots': [f'/taxii2/{key}/' for key in list_root_keys()] #dynamically build api roots defined in root endpoint
}

# MAY NEED TO AUTH BEFORE?
@router.get('/taxii2/', tags=['Discovery'])
async def get_discovery(request:Request =None, ):
    """
    provides metadata about the taxii server
    """
    # authenticate
    headers = dict(request.headers)
    from .root import list_root_keys
    api_roots = list_root_keys()
    authed = False

    for api_root in api_roots:
        try:
            misp.get_user_perms(headers=headers, api_root=api_root)
            authed = True
            break
        except Exception:
            continue

    if not authed:
        raise HTTPException(status_code=403, detail='The client does not have access to this resource')

    return discovery_info
