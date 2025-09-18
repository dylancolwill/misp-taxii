from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
import functions.misp as misp
import requests

router = APIRouter()

taxii_accept = "application/taxii+json;version=2.1"
taxii_content_type = "application/taxii+json;version=2.1"


@router.get("/taxii2/api1/collections/", tags=["Collections"])
async def get_collections(headers: dict = Depends(misp.get_headers)):
    """
    TAXII 2.1 Collections endpoint
    Returns all collections (mapped from MISP events)
    """
    try:
        # get all events
        misp_response = misp.query_misp_api("/events/index", headers=headers)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        detail = e.response.json() if e.response.headers.get("Content-Type") == "application/json" else str(e)
        if status_code in [401, 403]:
            raise HTTPException(status_code=status_code, detail=detail)
        else:
            raise HTTPException(status_code=500, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    # convert misp events to taxii collections
    collections = []
    for event in misp_response:
        collections.append({
            "id": str(event.get("id")),
            "title": event.get("info", "Unnamed Collection"),
            "description": event.get("Orgc", {}).get("name", ""),  # optional
            "can_read": True,   # assume api key allows read NEED TO FIX
            "can_write": False, # default
            "media_types": ["application/stix+json;version=2.1"]
        })

    return {
        "collections": collections
    }

