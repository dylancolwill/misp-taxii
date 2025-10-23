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
import logging
# import json
# import creds

##This File is based off of an old version of Collections due to this some parts may not be needed
##If that is the case it will be resolved

router = APIRouter()

logger = logging.getLogger(__name__)

#region utils
def check_unknown_filters(allowed_filters, request):
    # get query parameter keys from the request
    query_params = set(request.query_params.keys())

    # collect keys not allowed
    unknown_filters = [filter for filter in query_params if filter not in allowed_filters]
    if unknown_filters:
        logger.warning(f'Unknown filters detected: {unknown_filters}')
        raise HTTPException(
            status_code=400,
            detail=f'Unknown filter(s): {", ".join(unknown_filters)}'
        )

def fetch_collection_tag(collection_uuid, misp, conversion, headers, api_root):
    logger.debug(f'Fetching collection tag for UUID: {collection_uuid}')
    # get collection name from misp by matching passed uuid to tag id
    # misp tags are used to represent taxii collections
    
    # get all tags from misp
    misp_response = misp.query_misp_api('/tags/index', headers=headers, api_root=api_root)
    tags = misp_response.get('Tag', [])
    # find the tag name that matches the collection uuid after converting
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        logger.error(f'Collection UUID not found: {collection_uuid}')
        raise HTTPException(status_code=404, detail='Collection ID not found')
    logger.info(f'Found collection name: {tag["name"]} for UUID: {collection_uuid}')
    return tag['name']

def fetch_events(collection_name, misp, headers, added_after=None, next_token=None, limit =None, api_root=None):
    logger.debug(f'Fetching events for collection: {collection_name}')
    payload = {'tags': collection_name, 'returnFormat': 'json'}
    if added_after:
        payload['date_from'] = added_after #taxii added_after maps to misp date_from
    if next_token:
        payload['page'] = int(next_token) #next_token used as taxii page number
    if limit:
        payload['limit'] = int(limit)
    # send request to misp with additional search parameters
    response = misp.query_misp_api('/events/restSearch', method='POST', headers=headers, data=payload, api_root=api_root)
    logger.info(f'Fetched {len(response.get("response", []))} events from MISP for collection: {collection_name}')
    return response.get('response', [])

def convert_events_to_stix(events, conversion):
    # universal function to convert list of misp events to stix objects
    # need to normalise dict or bundle object into simple list of objects
    logger.debug(f'Converting {len(events)} MISP events to STIX objects')
    stix_objects = []
    for event in events:
        bundle = conversion.misp_to_stix(event['Event'])
        # if its a plain dict, assume its a dict bundle
        if isinstance(bundle, dict):
            stix_objects.extend(bundle.get('objects', []))
        else:
            stix_objects.extend(bundle.objects)
    logger.info(f'Converted to {len(stix_objects)} STIX objects')
    return stix_objects

def filter_stix_objects(
    objects, 
    object_id=None, object_type=None, version=None, spec_version=None, added_after=None
):
    logger.debug(f'Filtering STIX objects with provided criteria: id={object_id}, type={object_type}, version={version}, spec_version={spec_version}, added_after={added_after}')
    # custom filters not included in misp  
    def _filter(obj):
        # handle both dict and stix2 objects
        oid = obj.get('id') if isinstance(obj, dict) else getattr(obj, 'id', None)
        otype = oid.split('--')[0] if oid else None
        ver = obj.get('modified') if isinstance(obj, dict) else getattr(obj, 'modified', None)
        spec = obj.get('spec_version') if isinstance(obj, dict) else getattr(obj, 'spec_version', None)
        created = obj.get('created') if isinstance(obj, dict) else getattr(obj, 'created', None)

        # apply every filter if provided
        # need to do after repackaging to not damage bundle
        # if a filter is not set, will be ignored. 
        return (
            (not object_id or oid == object_id)
            and (not object_type or otype == object_type)
            and (not version or ver == version)
            and (not spec_version or spec == spec_version)
            and (not added_after or created >= added_after)
        )
    # only keep objects that pass all filters
    logger.info(f'Filtering complete. {len([obj for obj in objects if _filter(obj)])} objects match.')
    return [obj for obj in objects if _filter(obj)]

def paginate(objects, limit, next_token):
    # slice list with a given limit and next_token (start index)
    total = len(objects)
    start = int(next_token or 0)
    end = start + limit if limit is not None else total
    paged = objects[start:end] #current page of items
    more = (limit is not None and total > end) #check if more pages beyond current
    next_value = str(end) if more else None #if there is more, set next token to next start index
    logger.debug(f'Paginating objects: start={start}, end={end}, more={more}')
    return paged, more, next_value
#endregion utils

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/versions/', tags=['Objects'])
async def get_object_versions(
    collection_uuid: str,
    object_uuid: str,
    api_root: str,
    added_after: str = Query(None),
    limit: int = Query(None),
    next_token: str = Query(None),
    spec_version: str = Query(None, alias='match[spec_version]'),
    request: Request = None,
    response: Response = None
):  
    # reject unknown filters
    check_unknown_filters({'added_after', 'limit', 'next', 'match[spec_version]'}, request)
    # validate some filters
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        logger.warning(f'Invalid limit parameter: {limit}')
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after: #parse into datetime
        try:added_after_dt = datetime.fromisoformat(added_after)
        except ValueError:
            logger.warning(f'Invalid added_after parameter: {added_after}')
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    else:
        added_after_dt = None

    headers = dict(request.headers)
    # translate collection uuid to misp tag name
    collection_name = fetch_collection_tag(collection_uuid, misp, conversion, headers, api_root=api_root) 
    # get all misp events under tag name
    events = fetch_events(collection_name, misp, headers, added_after, next_token, limit, api_root=api_root)
    # convert events to stix objects
    stix_objects = convert_events_to_stix(events, conversion)
    
    # apply filters
    filtered = filter_stix_objects(stix_objects,object_id=object_uuid,object_type=None,version=None,spec_version=spec_version,added_after=added_after_dt)
    
    # get version timestamps, use modified otherwise created
    versions = []
    for obj in filtered:
        timestamp = getattr(obj, 'modified', getattr(obj, 'created', None)) if not isinstance(obj, dict) else obj.get('modified', obj.get('created', None))
        if timestamp:
            versions.append(timestamp)
    if not versions:
        logger.warning(f'No versions found for object UUID: {object_uuid}')
        raise HTTPException(status_code=404, detail='Object ID not found')

    versions.sort()
    
    # apply pagination by slicing list of version timestamps
    start = int(next_token or 0)
    end = start + limit if limit is not None else len(versions)
    paged_versions = versions[start:end]
    more = (limit is not None and len(versions) > end)
    next_value = str(end) if more else None

    # set return headers as taxii spec
    response.headers['X-TAXII-Date-Added-First'] = conversion.datetime_to_iso(min(versions))
    response.headers['X-TAXII-Date-Added-Last'] = conversion.datetime_to_iso(max(versions))
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    # package response
    result = {'versions': [conversion.datetime_to_iso(v) for v in paged_versions]}
    if limit is not None:
        result['more'] = more
        if more:
            result['next'] = next_value
    return result

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/objects/', tags=['Objects'])
async def get_objects(
    collection_uuid: str,
    api_root: str,
    added_after: str = Query(None, alias='added_after'),
    limit: int = Query(None, alias='limit'),
    next_token: str = Query(None, alias='next'),
    object_id: str = Query(None, alias='match[id]'),
    object_type: str = Query(None, alias='match[type]'),
    version: str = Query(None, alias='match[version]'),
    spec_version: str = Query(None, alias='match[spec_version]'),
    request: Request = None,
    response: Response = None
):
    # reject unknown filters
    check_unknown_filters({'added_after', 'limit', 'next', 'match[id]', 'match[type]', 'match[version]', 'match[spec_version]'}, request)
    # validate some filters
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        logger.warning(f'Invalid limit parameter: {limit}')
        raise HTTPException(status_code=400, detail='Invalid "limit" parameter. Must be a positive integer.')
    if added_after: #parse into datetime
        try: added_after = datetime.fromisoformat(added_after)
        except: 
            logger.warning(f'Invalid added_after parameter: {added_after}')
            raise HTTPException(status_code=400, detail='Invalid "added_after" parameter. Must be ISO date string.')
    
    headers = dict(request.headers)
    # translate collection uuid to misp tag name
    collection_name = fetch_collection_tag(collection_uuid, misp, conversion, headers, api_root=api_root) 
    # get all misp events under tag name
    events = fetch_events(collection_name, misp, headers, added_after, next_token, limit, api_root=api_root)
    # convert events to stix objects
    stix_objects = convert_events_to_stix(events, conversion)
    
    # apply filters
    filtered = filter_stix_objects(stix_objects, object_id, object_type, version, spec_version, added_after)
    # paginate filtered results
    paged, more, next_value = paginate(filtered, limit, next_token)
    
    # set return headers as taxii spec
    # for returned page if any objects present
    if paged:
        created_list = [obj.get('created') if isinstance(obj, dict) else getattr(obj, 'created', None) for obj in paged if obj.get('created') or getattr(obj, 'created', None)]
        if created_list:
            response.headers['X-TAXII-Date-Added-First'] = conversion.datetime_to_iso(min(created_list))
            response.headers['X-TAXII-Date-Added-Last'] = conversion.datetime_to_iso(max(created_list))
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'
    
    # package response
    result = {'objects': paged}
    if limit is not None:
        result['more'] = more
        if more: result['next'] = next_value
    return result

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/', tags=['Objects'])
async def get_object(
    collection_uuid: str,
    object_uuid: str,
    api_root: str,
    added_after: str = Query(None, alias='added_after'),
    limit: int = Query(None, alias='limit'),
    next_token: str = Query(None, alias='next'),
    # object_type: str = Query(None, alias='match[type]'),
    version: str = Query(None, alias='match[version]'),
    spec_version: str = Query(None, alias='match[spec_version]'),
    request: Request = None,
    response: Response = None
):
    # reject unknown filters
    check_unknown_filters({'added_after', 'limit', 'next', 'match[version]', 'match[spec_version]'}, request)
    # validate some filters
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        logger.warning(f'Invalid limit parameter: {limit}')
        raise HTTPException(status_code=400, detail="Invalid 'limit' parameter. Must be a positive integer.")
    if added_after: #parse into datetime
        try: added_after = datetime.fromisoformat(added_after)
        except: 
            logger.warning(f'Invalid added_after parameter: {added_after}')
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
        
    headers = dict(request.headers)
    # translate collection uuid to misp tag name
    collection_name = fetch_collection_tag(collection_uuid, misp, conversion, headers, api_root=api_root) 
    # get all misp events under tag name
    events = fetch_events(collection_name, misp, headers, added_after, next_token, limit, api_root=api_root)
    # convert events to stix objects
    stix_objects = convert_events_to_stix(events, conversion)
    
    # apply filters
    filtered = filter_stix_objects(stix_objects,object_id=object_uuid,object_type=None,version=version,spec_version=spec_version,added_after=added_after)
    # paginate filtered results
    paged, more, next_value = paginate(filtered, limit, next_token)
    
    # handle empty reponse
    # if not paged:
    #     raise HTTPException(status_code=404, detail='Object ID not found')
        
    # set return headers as taxii spec
    created_list = [
    obj.get('created') if isinstance(obj, dict) else getattr(obj, 'created', None)
    for obj in paged if (obj.get('created') if isinstance(obj, dict) else getattr(obj, 'created', None))]
    if created_list:
        response.headers['X-TAXII-Date-Added-First'] = conversion.datetime_to_iso(min(created_list))
        response.headers['X-TAXII-Date-Added-Last'] = conversion.datetime_to_iso(max(created_list))
    response.headers['Content-Type'] = 'application/taxii+json;version=2.1'

    # package response
    result = {'objects': paged}
    if limit is not None:
        result['more'] = more
        if more: result['next'] = next_value
    return result

@router.post('/taxii2/{api_root}/collections/{collection_uuid}/objects/', tags=['Objects'])
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

    _, perm_add =misp.get_user_perms(headers=headers, api_root=api_root) #check user perms
    if not perm_add:
        logging.warning(f'Permission denied for adding objects to collection {collection_uuid}')
        raise HTTPException(status_code=403, detail='The client does not have access to write to this objects resource')
    if headers.get('content-type') != 'application/taxii+json;version=2.1':
        logging.warning(f'Unsupported content type: {headers.get("content-type")}')
        raise HTTPException(status_code=415, detail='The client attempted to POST a payload with a content type the server does not support') 
    if int(headers.get('content-length', 0)) > get_content_size(api_root):
        logging.warning(f'Payload too large: {headers.get("content-length")}')
        raise HTTPException(status_code=413, detail='The POSTed payload exceeds the max_content_length of the API Root')

    # convert collection uuid to misp id
    collection_name = fetch_collection_tag(collection_uuid, misp, conversion, headers, api_root=api_root)
    # misp_response = misp.query_misp_api('/tags/index', headers=headers)
    # tags = misp_response.get('Tag', [])
    # tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    # if not tag:
    #     logging.error(f'Collection UUID not found: {collection_uuid}')
    #     raise HTTPException(status_code=404, detail='Collection ID not found')
    # collection_name = tag['name']
    
    # accept taxii envelope or stix bundle
    # if envelope, wrap objects in a stix bundle for processing
    if 'objects' in stix_bundle and stix_bundle.get('type') != 'bundle':
        stix_bundle = {
            'type': 'bundle',
            'id': f'bundle--{uuid.uuid4()}',
            'objects': stix_bundle['objects']
        }
    
    # convert dict to stix bundle if needed
    try:
        bundle = stix2.parse(stix_bundle, allow_custom=True)
        # if not isinstance(bundle, stix2.Bundle):
        #     raise ValueError('Provided data is not a STIX2 Bundle object')
        # check for supported stix version
        if getattr(bundle, 'spec_version', '2.1') != '2.1':
            raise HTTPException(status_code=422, detail='Only STIX 2.1 is supported by this TAXII server.')
        # check objects for supported spec_version
        for obj in getattr(bundle, 'objects', []):
            spec_version = getattr(obj, 'spec_version', None) if not isinstance(obj, dict) else obj.get('spec_version')
            if spec_version and spec_version != '2.1':
                raise HTTPException(status_code=422, detail='Only STIX 2.1 objects are supported by this TAXII server.')
    except Exception as e:
        raise HTTPException(status_code=422, detail=f'Unprocessable content')
    
    # convert stix bundle to misp event
    # try:
    #     parser = InternalSTIX2toMISPParser()
    #     parser.load_stix_bundle(bundle)
    #     parser.parse_stix_bundle()
    #     # print(bundle.objects)
    #     misp_event = parser.misp_events
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f'Failed to convert STIX to MISP {e}')
    
    misp_event =conversion.stix_to_misp(bundle)
    
    # attach collection tag to event
    if hasattr(misp_event, 'Tag'):
        misp_event.Tag.append({'name': collection_name})
    else:
        misp_event['Tag'] = [{'name': collection_name}]
        
    # print(parser.misp_events)
    
    # event = parser.misp_events
    # print('Event info:', event.info)
    # print('Number of attributes:', len(event.attributes))
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
    object_ids = []
    for obj in getattr(bundle, 'objects', []) or []:
        if isinstance(obj, dict):
            oid = obj.get('id')
        else:
            oid = getattr(obj, 'id', None)
        if oid:
            object_ids.append(oid)
       
    try:
        result = misp.query_misp_api('/events/add', method='POST', headers=headers, data=event_json, api_root=api_root)

        # taxii fields for successful upload
        success_count =len(object_ids)
        successes =[{'id': oid} for oid in object_ids] #list of successful object ids
        failure_count = 0
        pending_count =0
        status ='complete'
    except requests.exceptions.HTTPError as e:
        # print(e)
        if e.response.status_code==403: 
            logging.warning(f'Permission denied for adding objects to collection {collection_uuid}')
            raise HTTPException(status_code=403, detail='The client does not have access to write to this objects resource')
        
        #cannot add objects with same uuid, throws errors with different origins and codes
        if e.response.status_code ==404: 
            logging.warning(f'Attempted to add object with the same UUID as another object already in MISP: {collection_uuid}')
            raise HTTPException(status_code=400, detail='Atempted to add object with the same UUID as another object already in MISP')

        # taxii fields for failed upload
        status = 'pending'
        success_count =0
        successes =[]
        failure_count =len(object_ids)
        pending_count =0
        
        result = {}
        
    try:
        if 'Event' not in result:
            logging.error('Failed to add event to MISP, unknown error')
            raise HTTPException(status_code=400, detail='Failed to add event to MISP, unknown error')
    except requests.exceptions.HTTPError as e:
        if e.status_code==403: #cannot add objects with same uuid, throws errors with different origins and codes
            logging.warning(f'Attempted to add object with the same UUID as another object already in MISP: {collection_uuid}')
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