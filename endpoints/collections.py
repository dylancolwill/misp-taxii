from fastapi import APIRouter, Depends, Request, HTTPException
import functions.misp as misp
import requests
import uuid

router = APIRouter()

@router.get('/taxii2/api1/collections/', tags=['Collections'])
def get_misp_collections(headers= None):
    """
    Fetch all MISP tags and convert them into TAXII 2.1 collections.
    Each tag becomes a collection.
    """
    print('start')
    try:
        response = misp.query_misp_api('/tags/index', headers=headers)
        # response.raise_for_status()
        print(response)
        tags = response.get('Tag')  #returns a list of tag dicts
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'MISP request failed: {e}')

    can_write=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    collections = []
    for tag in tags:
        collections.append({
            'id': str(uuid.uuid5(uuid.NAMESPACE_OID, str(tag['id']))), #convert id to uuid
            'title': tag['name'],
            'description': tag.get('description', None),
            'can_read': True, #if user got this far through request, can access
            'can_write': can_write,
            'media_types': ['application/stix+json;version=2.1']
        })
    
    return collections

@router.get('/taxii2/api1/collections/{collection_id}', tags=['Collections'])
def get_misp_collections(collection_id = int, headers= None):
    """
    Fetch all MISP tags and convert them into TAXII 2.1 collections.
    Each tag becomes a collection.
    """
    print('start')
    try:
        response = misp.query_misp_api('/tags/index', headers=headers)
        # response.raise_for_status()
        print(response)
        tags = response.get('Tag')  #returns a list of tag dicts
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'MISP request failed: {e}')

    can_write=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    # find matching tag
    tag = next((t for t in tags if str(t['id']) == collection_id), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection not found')
    
    return {
        'id': str(uuid.uuid5(uuid.NAMESPACE_OID, str(tag['id']))), #convert id to uuid
        'title': tag['name'],
        'description': tag.get('description', None),
        'can_read': True, #if user got this far through request, can access
        'can_write': can_write,
        'media_types': ['application/stix+json;version=2.1']
    }