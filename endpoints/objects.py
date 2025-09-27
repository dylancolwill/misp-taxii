from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
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
        print("Broke Before Conversion, Object")
        stixObject = conversion.misp_to_stix(event)
        print("Passed STIX Conversion, Object")
        print(stixObject)
        objects.append(stixObject)

    # return objects

"""Tag association section, this section aim to find the Tags on the objects"""


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
    """
    returns all versions of an object, given collection and object uuid
    since taxii requires uuid but misp uses id, need to fetch all tags and filter in code, cannot query for id
    """
    #  extract headers from initial request
    headers = dict(request.headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    misp_response = misp.query_misp_api('/tags/index', headers=headers)
    tags = misp_response.get('Tag')  #returns a list of tag dicts
    
    # find matching tag, need to convert each collection id to uuid
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection not found')
    collection_name = tag['name'] #used to fetch matching events
    # print(collection_name)
    
    # setup payload to use in misp request
    print('getting related misp events...')
    payload = {
        'tags': collection_name,
        'returnFormat': 'json'
    }
    
    # apply filters where possible
    if added_after:
        payload['date_from'] = added_after
    if limit:
        payload['limit'] = limit
    if next_token:
        payload['page'] = int(next_token) 
    
    # query misp for events matching this collection using restSearch
    misp_response = misp.query_misp_api('/events/restSearch', method='POST',  headers=headers, data=payload)
    events = misp_response.get('response', [])
    
    # convert events into stix bundles 
    object_bundles = [conversion.misp_to_stix(event['Event']) for event in events]
    print("Passed STIX Conversion")    
           
    # collect all versions of requested stix
    versions = []
    for bundle in object_bundles:
        for obj in bundle.objects:
            if obj.id == object_uuid: #match object uuid
                timestamp = getattr(obj, 'modified', obj.created) #use modified otherwise created, per specs
                versions.append(timestamp)

    if not versions:
        raise HTTPException(status_code=404, detail='Object not found')

    # sort chronologically
    versions.sort()
        
    # include taxii headers per specs
    response.headers['X-TAXII-Date-Added-First'] = min(versions).isoformat()
    response.headers['X-TAXII-Date-Added-Last'] = max(versions).isoformat()
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    # return list of versions
    return {"versions": [v for v in versions]} #have to loop, breaks just returning list ?