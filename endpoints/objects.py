from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
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
    
@router.get('/taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/versions/', tags=['Objects'])
async def get_object_versions(
    collection_uuid: str,
    object_uuid: str,
    added_after: str = Query(None),
    limit: int = Query(None),
    next_token: str = Query(None),
    spec_version: str = Query(None, alias='match[spec_version]'),
    request: Request = None,
    response: Response = None
):
    headers = dict(request.headers)
    
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
    
    print('getting related misp events...')
    payload = {
        'tags': collection_name,
        'returnFormat': 'json'
    }
    
    if added_after:
        payload['date_from'] = added_after
    if limit:
        payload['limit'] = limit
    if next_token:
        payload['page'] = int(next_token) 
    
    misp_response = misp.query_misp_api('/events/restSearch', method='POST',  headers=headers, data=payload)
    events = misp_response.get('response', [])
    
    object_bundles = [conversion.misp_to_stix(event['Event']) for event in events]
    print("Passed STIX Conversion")    
        
    print(object_bundles)
    
    versions = []
    for bundle in object_bundles:
        for obj in bundle.objects:
            if obj.id == object_uuid:
                # use modified otherwise created, per specs
                timestamp = getattr(obj, 'modified', obj.created)
                versions.append(timestamp)

    if not versions:
        raise HTTPException(status_code=404, detail='Object not found')

    versions.sort()
        
    response.headers['X-TAXII-Date-Added-First'] = min(versions).isoformat()
    response.headers['X-TAXII-Date-Added-Last'] = max(versions).isoformat()
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    return {"versions": [v for v in versions]}