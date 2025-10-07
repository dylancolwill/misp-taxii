from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
import functions.misp as misp
import requests
from misp_stix_converter import MISPtoSTIX21Parser
import functions.conversion  as conversion
import endpoints.collections as collections
from datetime import datetime
# import creds

##This File is based off of an old version of Collections due to this some parts may not be needed
##If that is the case it will be resolved

router = APIRouter()

print("before router")

def check_unknown_filters(allowed_filters, request):
    # get query parameter keys from the request
    query_params = set(request.query_params.keys())

    # check for unsupported filters
    unknown_filters = [filter for filter in query_params if filter not in allowed_filters]
    if unknown_filters:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown filter(s): {', '.join(unknown_filters)}"
        )

        
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
    
    # verify filters are correct
    check_unknown_filters({'added_after', 'limit', 'next_token', 'match[spec_version]'}, request)
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after is not None:
        try:
            datetime.fromisoformat(added_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    
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
    
    # pagination
    more = False
    next_value = None
    start = int(next_token or 0)
    end = start + limit if limit is not None else len(versions)
    paged_versions = versions[start:end]
    if limit is not None and len(versions) > end:
        more = True
        next_value = str(end)
        
    # include taxii headers per specs
    response.headers['X-TAXII-Date-Added-First'] = min(versions).isoformat()
    response.headers['X-TAXII-Date-Added-Last'] = max(versions).isoformat()
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    # list of versions with taxii envelope
    result = {'versions': [v for v in paged_versions]}
    if limit is not None:
        result['more'] = more
        if more:
            result['next'] = next_value
    
    # return list of versions
    return result

@router.get("/taxii2/{api_root}/collections/{collection_uuid}/objects/", tags=["Objects"])
async def get_objects(
    collection_uuid: str,
    added_after: str = Query(None, alias='added_after'),
    limit: int = Query(None, alias='limit'),
    next_token: str = Query(None, alias='next'), #taxii next
    object_id: str = Query(None, alias='match[id]'),
    object_type: str = Query(None, alias='match[type]'), #dont think misp has these filters?
    version: str = Query(None, alias='match[version]'),
    spec_version: str = Query(None, alias='match[spec_version]'),
    request: Request = None,
    response: Response = None
):
    check_unknown_filters({'added_after', 'limit', 'next', 'match[id]', 'match[type]', 'match[version]', 'match[spec_version]'
    }, request)
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after is not None:
        try:
            datetime.fromisoformat(added_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    
    
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
    
    # setup payload to use in misp request
    print('getting related misp events...')
    payload = {
        'tags': collection_name,
        'returnFormat': 'json'
    }
    
    # apply filters where possible
    if added_after:
        payload['date_from'] = added_after
    if next_token:
        payload['page'] = int(next_token) 
    
    # query misp for events matching this collection using restSearch
    misp_response = misp.query_misp_api('/events/restSearch', method='POST',  headers=headers, data=payload)
    events=misp_response['response']
    
    # convert each misp event into stix
    objects,first,last=[],[],[]
    for event in events:
        event=event['Event'] #misp wraps event inside, {'Event': {}}
        # convert misp events into STIX
        stixObject = conversion.misp_to_stix(event) #call function to handle conversion
        print("Passed STIX Conversion")
        # date_added_list.append(objects.created)
        
        # unwrap stix objects from bundle and add to list for return
        if isinstance(stixObject, dict):
            objects.extend(stixObject.get('objects', []))
        else:
            objects.extend(stixObject.objects)
            
        # collect created and modified timestamps for return header
        for obj in objects:
            for attr, lst in [('created', first), ('modified', last)]:
                ts = getattr(obj, attr, obj.get(attr))  # get from stix
                if ts:
                    lst.append(ts.isoformat() if hasattr(ts, 'isoformat') else str(ts))
                    
    # custom filters not included in misp
    # need to do after repackaging to not damage bundle
    # if a filter is not set, will be ignored. 
    filtered_objects = [
        obj for obj in objects #creates a new list and loopes over every object
        if (not object_id or obj['id'] == object_id) 
        and (not object_type or obj['id'].split('--', 1)[0] == object_type) #extract stix type from object id
        and (not version or obj['version'] == version)
        #for each object, checks the if condition, if true is included in new list, if false skips
        # if no filters are applied, every condition is true, all are included in list
    ]
    
    objects=filtered_objects
    
    more = False
    next_value = None
    total_objects = len(objects)
    if limit is not None:
        if total_objects > limit:
            more = True
            objects = objects[:limit]
            # increment page or offset
            next_value = str(int(next_token or 0) + 1)
        else:
            objects = objects[:limit]

    print("passed final")
    print(objects)

    print('complete')
    
    if first and last:
        response.headers['X-TAXII-Date-Added-First'] = min(first)
        response.headers['X-TAXII-Date-Added-Last'] = max(last)
    
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    # add more to envelope if paginating
    result = {'objects': objects}
    if limit is not None:
        result['more'] = more
        if more:
            result['next'] = next_value
    
    return result

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/', tags=['Objects'])
async def get_object(
    collection_uuid: str,
    object_uuid: str,
    added_after: str = Query(None, alias='added_after'),
    limit: int = Query(None, alias='limit'),
    next_token: str = Query(None, alias='next'), #taxii next
    request: Request = None,
    response: Response = None
):
    """
    returns all versions of an object, given collection and object uuid
    since taxii requires uuid but misp uses id, need to fetch all tags and filter in code, cannot query for id
    """
    check_unknown_filters({'added_after', 'limit', 'next'}, request)
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after is not None:
        try:
            datetime.fromisoformat(added_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    
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
    
    # query misp for events matching this collection using restSearch
    misp_response = misp.query_misp_api('/events/restSearch', method='POST',  headers=headers, data=payload)
    events = misp_response.get('response', [])
    
    # convert events into stix bundles 
    stix_objects = []
    for event in events:
        bundle = conversion.misp_to_stix(event['Event'])
        if isinstance(bundle, dict):
            stix_objects.extend(bundle.get('objects', []))
        else:
            stix_objects.extend(bundle.objects)
    print("Passed STIX Conversion")    
           
    # collect all versions of requested stix
    requestedObject=None
    # for bundle in stix_objects:
    for obj in stix_objects:
        if obj.id == object_uuid: #match object uuid
            timestamp = getattr(obj, 'modified', obj.created) #use modified otherwise created, per specs
            requestedObject = obj

    # if object not found raise
    if requestedObject is None:
        raise HTTPException(status_code=404, detail=f'Object not found')

    # include taxii headers per specs
    response.headers['X-TAXII-Date-Added-First'] = getattr(requestedObject, 'created', None).isoformat()
    response.headers['X-TAXII-Date-Added-Last'] = getattr(requestedObject, 'modified', None).isoformat()
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    return {'objects':[requestedObject]}  

@router.post("/taxii2/{api_root}/collections/{collection_uuid}/objects/", tags=["Objects"])
async def get_objects(
    collection_uuid: str,
    object_uuid: str,
    request: Request = None,
    response: Response = None
):
    pass