from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List
import functions.misp as misp
import requests
from misp_stix_converter import MISPtoSTIX21Parser
import functions.conversion  as conversion
import endpoints.collections as collections
import creds
import pprint
##This File is based off of an old version of Collections due to this some parts may not be needed
##If that is the case it will be resolved

router = APIRouter()

taxii_accept = "application/taxii+json;version=2.1"
taxii_content_type = "application/taxii+json;version=2.1"


print("before router")
@router.post("/taxii2/api1/collections/objects/", tags=["Objects"])
async def post_objects(headers: dict = Depends(misp.get_headers)):
    print("after router")

    try:
        # get all events
        print("before misp response")
        misp_response = misp.query_misp_api("/events/index", headers=headers)
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
        raise HTTPException(status_code=500, detail=str(e))

    #Take each event and convert it separately, then append it to the list
    objects = []
    for event in misp_response:
        #convert misp events into STIX
        print("Broke Before Conversion")
        stixObject = conversion.misp_to_stix(event)
        print("Passed STIX Conversion")
        print(stixObject)
        objects.append(stixObject)

    # return objects

    """
    since taxii requires uuid not id, need to fetch all tags and filter in code, cannot query for id
    """
        
    print('getting all misp tags...')
    misp_response = misp.query_misp_api('/tags/index', headers=headers)
    tags = misp_response.get('Tag')  #returns a list of tag dicts
    
    # find matching tag, need to convert each collection id to uuid
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection not found')
    collection_name = tag['name']
    # print(collection_name)

    return {
        "objects": stixObject
    }