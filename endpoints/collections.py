from fastapi import APIRouter, Depends, Request, HTTPException
import functions.misp as misp
import functions.conversion as conversion
import requests
import uuid

router = APIRouter()

@router.get('/taxii2/api1/collections/', tags=['Collections'])
def get_misp_collections(headers= None):
    """
    Fetch all MISP tags and convert them into TAXII 2.1 collections.
    Each tag becomes a collection.
    """
    print('getting all misp tags...')
    response = misp.query_misp_api('/tags/index', headers=headers)
    tags = response.get('Tag')  #returns a list of tag dicts

    can_write=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    collections = []
    for tag in tags:
        collections.append({
            'id': conversion.str_to_uuid(tag['id']), #convert id to uuid
            'title': tag['name'],
            'description': tag.get('description', None),
            'can_read': True, #if user got this far through request, can access
            'can_write': can_write,
            'media_types': ['application/stix+json;version=2.1']
        })
    
    return collections

@router.get('/taxii2/api1/collections/{collection_uuid}', tags=['Collections'])
def get_misp_collections(collection_uuid = int, headers= None):
    """
    since taxii requires uuid not id, need to fetch all tags and filter in code, cannot query for id
    """
    print('getting all misp tags...')
    response = misp.query_misp_api('/tags/index', headers=headers)
    tags = response.get('Tag')  #returns a list of tag dicts

    can_write=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    # find matching tag
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection not found')
    
    return {
        'id': conversion.str_to_uuid(tag['id']), #convert id to uuid
        'title': tag['name'],
        'description': tag.get('description', None),
        'can_read': True, #if user got this far through request, can access
        'can_write': can_write,
        'media_types': ['application/stix+json;version=2.1']
    }