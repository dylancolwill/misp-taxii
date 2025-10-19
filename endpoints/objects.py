from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response, Body
import functions.misp as misp
import requests
from misp_stix_converter import MISPtoSTIX21Parser, InternalSTIX2toMISPParser
import functions.conversion  as conversion
import endpoints.collections as collections
import stix2
from datetime import datetime, timezone
import uuid
from .root import get_content_size
# import json
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
    try:
        misp_response = misp.query_misp_api('/tags/index', headers=headers)
        tags = misp_response.get('Tag')  #returns a list of tag dicts
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            raise HTTPException(status_code=403, detail='The client does not have access to this object resource')
    
    # find matching tag, need to convert each collection id to uuid
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection ID not found')
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
        raise HTTPException(status_code=404, detail='Object ID not found')

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
    # validate filters
    check_unknown_filters({'added_after', 'limit', 'next', 'match[id]', 'match[type]', 'match[version]', 'match[spec_version]'}, request)
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after is not None:
        try:
            added_after =datetime.fromisoformat(added_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    
    
     #  extract headers from initial request
    headers = dict(request.headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    try:
        misp_response = misp.query_misp_api('/tags/index', headers=headers)
        tags = misp_response.get('Tag')  #returns a list of tag dicts
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            raise HTTPException(status_code=403, detail='The client does not have access to this object resource')
    
    # find matching tag, need to convert each collection id to uuid
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection ID not found')
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
            _objects = stixObject.get('objects', [])
        else:
            _objects = stixObject.objects
        # extend the list with only the newly unwrapped objects 
        objects.extend(_objects)
            
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
    # print(objects) 

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
    version: str = Query(None, alias='match[version]'),
    spec_version: str = Query(None, alias='match[spec_version]'),
    request: Request = None,
    response: Response = None
):
    """
    returns all versions of an object, given collection and object uuid
    since taxii requires uuid but misp uses id, need to fetch all tags and filter in code, cannot query for id
    """
    check_unknown_filters({'added_after', 'limit', 'next', 'match[version]', 'match[spec_version]'}, request)
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after is not None:
        try:
            added_after=datetime.fromisoformat(added_after)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    
    #  extract headers from initial request
    headers = dict(request.headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    try:
        misp_response = misp.query_misp_api('/tags/index', headers=headers)
        tags = misp_response.get('Tag',[])  #returns a list of tag dicts
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            raise HTTPException(status_code=403, detail='The client does not have access to this object resource')
    
    # find matching tag, need to convert each collection id to uuid
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection ID not found')
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
    try:
        misp_response = misp.query_misp_api('/events/restSearch', method='POST',  headers=headers, data=payload)
        events = misp_response.get('response', [])
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            raise HTTPException(status_code=403, detail='The client does not have access to this object resource')
    
    # convert events into stix bundles 
    stix_objects = []
    for event in events:
        bundle = conversion.misp_to_stix(event['Event'])
        if isinstance(bundle, dict):
            stix_objects.extend(bundle.get('objects', []))
        else:
            stix_objects.extend(bundle.objects)
    print("Passed STIX Conversion")   
    
    # custom filters not included in misp
    # need to do after repackaging to not damage bundle
    # if a filter is not set, will be ignored. 
    filtered_objects = [
        obj for obj in stix_objects
        if getattr(obj, 'id', obj.get('id', None)) == object_uuid
        and (not version or getattr(obj, 'version', obj.get('version', None)) == version)
        and (not spec_version or getattr(obj, 'spec_version', obj.get('spec_version', None)) == spec_version)
        and (not added_after or getattr(obj, 'created', obj.get('created', None)) >= added_after)
        #for each object, checks the if condition, if true is included in new list, if false skips
        # if no filters are applied, every condition is true, all are included in list
    ]
      
    # pagination
    more = False
    next_value = None
    total_objects = len(filtered_objects)
    start = int(next_token or 0)
    end = start + limit if limit is not None else total_objects
    paged_objects = filtered_objects[start:end]
    if limit is not None and total_objects > end:
        more = True
        next_value = str(end)
           
    # collect all versions of requested stix
    requestedObject=None
    # for bundle in stix_objects:
    for obj in stix_objects:
        if obj.id == object_uuid: #match object uuid
            timestamp = getattr(obj, 'modified', obj.created) #use modified otherwise created, per specs
            requestedObject = obj

    # if object not found raise
    if requestedObject is None:
        raise HTTPException(status_code=404, detail=f'Object ID not found')

    # return headers based on returned objects
    # indicate earlist and latest created/modified dates
    if paged_objects:
        created_list = [getattr(obj, 'created', obj.get('created', None)) for obj in paged_objects if getattr(obj, 'created', obj.get('created', None))]
        modified_list = [getattr(obj, 'modified', obj.get('modified', None)) for obj in paged_objects if getattr(obj, 'modified', obj.get('modified', None))]
        if created_list:
            response.headers['X-TAXII-Date-Added-First'] = min(created_list).isoformat() if hasattr(min(created_list), 'isoformat') else str(min(created_list))
        if modified_list:
            response.headers['X-TAXII-Date-Added-Last'] = max(modified_list).isoformat() if hasattr(max(modified_list), 'isoformat') else str(max(modified_list))
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'

    # build taxii envelope
    result = {'objects': paged_objects}
    if limit is not None:
        result['more'] = more
        if more:
            result['next'] = next_value

    return result

@router.post("/taxii2/{api_root}/collections/{collection_uuid}/objects/", tags=["Objects"])
async def add_objects(
    collection_uuid: str,
    api_root: str,
    request: Request = None,
    response: Response = None,
    stix_bundle: dict = Body(...)
    ):
    #  extract headers from initial request
    headers = dict(request.headers)
    # print(headers)
    
    # checks before processing
    
    _, perm_add =misp.get_user_perms(headers=headers) #check user perms
    if not perm_add:
        raise HTTPException(status_code=403, detail='The client does not have access to write to this objects resource')
    if headers.get('content-type') != 'application/taxii+json;version=2.1':
        raise HTTPException(status_code=415, detail='The client attempted to POST a payload with a content type the server does not support') 
    if int(headers.get('content-length', 0)) > get_content_size(api_root):
        raise HTTPException(status_code=413, detail='The POSTed payload exceeds the max_content_length of the API Root')

    # convert collection uuid to misp id
    misp_response = misp.query_misp_api('/tags/index', headers=headers)
    tags = misp_response.get('Tag', [])
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection ID not found')
    collection_name = tag['name']
    
    # convert dict to stix bundle if needed
    try:
        bundle = stix2.parse(stix_bundle, allow_custom=True)
        if not isinstance(bundle, stix2.Bundle):
            raise ValueError("Provided data is not a STIX2 Bundle object")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Invalid STIX bundle: {e}')
    
    # convert stix bundle to misp event
    try:
        parser = InternalSTIX2toMISPParser()
        parser.load_stix_bundle(bundle)
        parser.parse_stix_bundle()
        # print(bundle.objects)
        misp_event = parser.misp_events
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to convert STIX to MISP {e}')
    
    # attach collection tag to event
    if hasattr(misp_event, 'Tag'):
        misp_event.Tag.append({'name': collection_name})
    else:
        misp_event['Tag'] = [{'name': collection_name}]
        
    # print(parser.misp_events)
    
    # event = parser.misp_events
    # print("Event info:", event.info)
    # print("Number of attributes:", len(event.attributes))
    # for attr in event.attributes:
    #     print(attr.type, attr.value)


    # push event to misp
    event_json = misp_event.to_json() if hasattr(misp_event, 'to_json') else misp_event
    
    import json
    # ensure event_json is a dict, not string
    if isinstance(event_json, str):
        event_json = json.loads(event_json)
    # pack inside Event if not already
    if 'Event' not in event_json:
        event_json = {'Event': event_json}
        
    # get all object ids from incoming bundle
    object_ids = [obj['id'] for obj in bundle.objects if isinstance(obj, dict) and 'id' in obj]
       
    try:
        result = misp.query_misp_api('/events/add', method='POST', headers=headers, data=event_json)

        # taxii fields for successful upload
        success_count =len(object_ids)
        successes =[{'id': oid} for oid in object_ids] #list of successful object ids
        failure_count = 0
        pending_count =0
        status ='complete'
    except requests.exceptions.HTTPError as e:
        # print(e)
        if e.response.status_code==403: raise HTTPException(status_code=403, detail='The client does not have access to write to this objects resource')
        
        #cannot add objects with same uuid, throws errors with different origins and codes
        if e.response.status_code ==404: raise HTTPException(status_code=400, detail='Atempted to add object with the same UUID as another object already in MISP')
        
        # taxii fields for failed upload
        status = 'pending'
        success_count =0
        successes =[]
        failure_count =len(object_ids)
        pending_count =0
        
        result = {}
        
    try:
        if 'Event' not in result:
            raise HTTPException(status_code=400, detail='Failed to add event to MISP, unknown error')
    except requests.exceptions.HTTPError as e:
        if e.status_code==403: #cannot add objects with same uuid, throws errors with different origins and codes
            raise HTTPException(status_code=400, detail='Duplicate objects')

    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    response.status_code = 202 #successful upload code
    
    return {
        'id': str(uuid.uuid4()),
        'status': status,
        'request_timestamp': datetime.now(timezone.utc).isoformat(timespec ='milliseconds'),
        'total_count': len(object_ids),
        'success_count': success_count,
        'successes': successes,
        'failure_count': failure_count,
        'pending_count': pending_count
    }