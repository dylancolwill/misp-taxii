from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
import functions.misp as misp
import requests
from misp_stix_converter import MISPtoSTIX21Parser
import functions.conversion  as conversion

router = APIRouter()

taxii_accept = "application/taxii+json;version=2.1"
taxii_content_type = "application/taxii+json;version=2.1"



@router.get("/taxii2/api1/collections/1/objects/", tags=["Objects"])
async def get_collections(headers: dict = Depends(misp.get_headers)):


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


     
    for event in misp_response:
    #convert misp event into STIX and bundle them - Lewis Testing in here b'cause he can't be bothered to make a new file
        stixObject = conversion.misp_to_stix(event[0])
        print(stixObject)

    return {
        "objects": stixObject
    }