from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
import functions.misp as misp
import functions.conversion as conversion
import requests
from datetime import datetime
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/manifests', tags=['Manifests'])
def get_manifests(collection_uuid: str,
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
    """
    takes collection uuid and returns metadata for stix objects in that collection.
    since taxii requires uuid but misp uses id, need to fetch all tags and filter in code, cannot query for id
    """
    #  extract headers from initial request
    headers = dict(request.headers)
    
    # query misp for all tags using headers
    logger.debug(f'Fetching collections')
    try:
        misp_response = misp.query_misp_api('/tags/index', headers=headers)
        tags = misp_response.get('Tag')  #returns a list of tag dicts
        logger.info(f'Fetched {len(tags) if tags else 0} tags from MISP')
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            logger.warning('Permission denied for accessing collections')
            raise HTTPException(status_code=403, detail='The client does not have access to this manifest resource')
    
    # find matching tag, need to convert each collection id to uuid
    logger.debug(f'Fetching collection tag for UUID: {collection_uuid}')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        logger.error(f'Collection UUID not found: {collection_uuid}')
        raise HTTPException(status_code=404, detail='Collection ID not found')
    collection_name = tag['name'] #used to fetch matching events
    # print(collection_name)
    
    # setup payload to use in misp request
    logger.debug(f'Fetching events for collection: {collection_name}')
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
    events=misp_response['response']

    logger.info(f'Fetched {len(events)} events from MISP for collection: {collection_name}')

    # convert each misp event into stix
    logger.debug(f'Converting {len(events)} MISP events to STIX objects')
    objects = []
    for event in events:
        event=event['Event'] #misp wraps event inside, {'Event': {}}
        stixObject = conversion.misp_to_stix(event) #call function to handle conversion
        objects.append(stixObject)
        
    # # custom filters not included in misp
    # _objects=objects['objects'] #extract list of stix objects in bundle
    # if object_id:
    #     for object in objects: #loop through objects dict key
    #         print(object['id'])    
            
    
    #repackage as manifests according to taxii spec
    manifests=[]
    date_added_list = []
    for bundle in objects:  # each item is a stix bundle
        for obj in bundle.objects:
            if obj.type != 'identity': #identity not needed 
                date_added =getattr(obj, 'created', None)
                if (date_added ==None):
                    continue  #skip objects without created date, per spec
                manifests.append({
                    'id': obj.id,
                    'date_added': date_added,
                    'version': getattr(obj, 'modified', obj.created),  # use modified if exists, else created
                    'media_type': 'application/stix+json;version=2.1'
                })
                date_added_list.append(obj.created) 
              
    # added_after as datetime if provided
    if added_after:
        try:
            added_after = datetime.fromisoformat(added_after)
        except ValueError:
            logger.error(f'Invalid added_after parameter: {added_after}')
            raise HTTPException(status_code=400, detail="Invalid 'added_after' parameter. Must be ISO date string.")
    else:
        added_after = None              
        
    # custom filters not included in misp
    # need to do after repackaging to not damage bundle
    # if a filter is not set, will be ignored. 
    filtered_manifests = [
        obj for obj in manifests #creates a new list and loopes over every object
        if (not object_id or obj['id'] == object_id) 
        and (not object_type or obj['id'].split('--', 1)[0] == object_type) #extract stix type from object id
        and (not version or obj['modified'] == version)
        and (not spec_version or obj.get('spec_version') == spec_version)
        and (not added_after or obj['date_added'] >= added_after)
        #for each object, checks the if condition, if true is included in new list, if false skips
        # if no filters are applied, every condition is true, all are included in list
    ]
    
    logger.info(f'Filtering complete. {len(filtered_manifests)} manifests match.')    
    manifests=filtered_manifests
    
    # taxii pagination
    more = False
    next_value = None
    start = int(next_token or 0)
    end = start + limit if limit is not None else len(manifests)
    paged_manifests = manifests[start:end]
    if limit is not None and len(manifests) > end:
        more = True
        next_value = str(end)
        
    # add required response headers per spec
    if date_added_list:
        response.headers['X-TAXII-Date-Added-First'] = min(date_added_list).isoformat()
        response.headers['X-TAXII-Date-Added-Last'] = max(date_added_list).isoformat()
    
    # list of object metadata with taxii envelope
    result = {'objects': paged_manifests}
    if limit is not None:
        result['more'] = more
        if more:
            result['next'] = next_value

    return result