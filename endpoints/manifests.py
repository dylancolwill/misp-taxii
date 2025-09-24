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
    since taxii requires uuid not id, need to fetch all tags and filter in code, cannot query for id
    """
    
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
    events=misp_response['response']
    
    print(events,'\n')
    
    objects = []
    
    for event in events:
        event=event['Event']
        print(event)
        # convert misp events into STIX
        stixObject = conversion.misp_to_stix(event)
        #stixObject = conversion.json_to_stix(event)
        print("Passed STIX Conversion")
        print(stixObject)
        objects.append(stixObject)
    print(objects)
    
    
    
    manifests = []
    date_added_list = []
    # for event in objects:
    #     date_added_list.append(event['Event']['date']) #prepare for response header required in taxii spec
    #     manifests.append({
    #         'id': event['Event']['uuid'], #NEED TO INCLUDE STIX OBJECT TYPE
    #         'date_added': event['Event']['date'],
    #         'version': event['Event']['timestamp'], #taxii spec states to use created timestamp if no version
    #         'media_type': 'application/stix+json;version=2.1'
    #     })
        
    print('complete')
    
    if date_added_list:
        response.headers['X-TAXII-Date-Added-First'] = min(date_added_list)
        response.headers['X-TAXII-Date-Added-Last'] = max(date_added_list)
    
    return {'objects':manifests}