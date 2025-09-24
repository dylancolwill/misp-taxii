from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
import functions.misp as misp
import requests
from misp_stix_converter import MISPtoSTIX21Parser
import functions.conversion  as conversion
import endpoints.collections as collections
import creds
import pprint
##This File is based off of Collections due to this some parts may not be needed
##If that is the case it will be resolved

router = APIRouter()

taxii_accept = "application/taxii+json;version=2.1"
taxii_content_type = "application/taxii+json;version=2.1"


print("before router")
@router.post("/taxii2/api1/collections/objects/", tags=["Objects"])
async def post_objects(headers: dict = Depends(misp.get_headers)): ##this might need to be changed
    print("after router")

    try:
        # get all events
        print("before misp response")
        misp_response = misp.query_misp_api("/events/index", headers=headers) #file breaks here
        print("after misp response")
        pprint.pp(misp_response)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        detail = e.response.json() if e.response.headers.get("Content-Type") == "application/json" else str(e)
        if status_code in [401, 403]:
            raise HTTPException(status_code=status_code, detail=detail)
        else:
            raise HTTPException(status_code=500, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) #its getting raised here


    objects = []
    for event in misp_response:
        #convert misp events into STIX
        print("Broke Before Conversion")
        stixObject = conversion.misp_to_stix(event)
        #stixObject = conversion.json_to_stix(event)
        print("Passed STIX Conversion")
        print(stixObject)
        objects.append(stixObject)

    # return objects

    return {
        "objects": stixObject
    }