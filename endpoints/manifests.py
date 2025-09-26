from fastapi import APIRouter, Depends, Request, HTTPException, Query, Response
import functions.misp as misp
import functions.conversion as conversion
import requests

router = APIRouter()

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/manifests', tags=['Manifests'])
def get_misp_manifests(collection_uuid: str,
    added_after: str = Query(None),
    limit: int = Query(None),
    next_token: str = Query(None), #taxii next
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
    events=misp_response['response']
    
    # convert each misp event into stix
    objects = []
    for event in events:
        event=event['Event'] #misp wraps event inside, {'Event': {}}
        # convert misp events into STIX
        stixObject = conversion.misp_to_stix(event) #call function to handle conversion
        #stixObject = conversion.json_to_stix(event)
        print("Passed STIX Conversion")
        objects.append(stixObject)
    
    #repackage as manifests according to taxii spec
    manifests=[]
    date_added_list = []
    for bundle in objects:  # each item is a stix bundle
        for obj in bundle.objects:
            if obj.type is not 'identity': #identity not needed 
                manifests.append({
                    'id': obj.id,
                    'date_added': obj.created ,
                    'version': getattr(obj, 'modified', obj.created),  # use modified if exists, else created
                    'media_type': 'application/stix+json;version=2.1'
                })
                date_added_list.append(obj.created)
            
    print('complete')
    
    # add required response headers per spec
    if date_added_list:
        response.headers['X-TAXII-Date-Added-First'] = min(date_added_list).isoformat()
        response.headers['X-TAXII-Date-Added-Last'] = max(date_added_list).isoformat()
    
    return {'objects':manifests}