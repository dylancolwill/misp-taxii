from fastapi import APIRouter, Depends, Request, HTTPException
import functions.misp as misp
import functions.conversion as conversion
import requests

router = APIRouter()

@router.get('/taxii2/{api_root}/collections/{collection_uuid}/manifests', tags=['Manifests'])
def get_misp_collections(collection_uuid, headers= None):
    """
    since taxii requires uuid not id, need to fetch all tags and filter in code, cannot query for id
    """
    print('getting all misp tags...')
    response = misp.query_misp_api('/tags/index', headers=headers)
    tags = response.get('Tag')  #returns a list of tag dicts

    can_write=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    # find matching tag, need to convert each collection id to uuid
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection not found')
    collection_name = tag['name']
    # print(collection_name)
    
    print('getting related misp events...')
    payload = {
        "tags": collection_name,
        "returnFormat": "json"
    }
    response = misp.query_misp_api('/events/restSearch', method="POST",  headers=headers, data=payload)
    events=response['response']
    
    manifests = []
    for event in events:
        manifests.append({
            'id': event['Event']['uuid'], #NEED TO INCLUDE STIX OBJECT TYPE
            'date_added': event['Event']['date'],
            'version': event['Event']['timestamp'], #taxii spec states to use created timestamp if no version
            'media_types': 'application/stix+json;version=2.1'
        })
    
    return manifests