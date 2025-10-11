from fastapi import APIRouter, Depends, Request, HTTPException, Response
import functions.misp as misp
import functions.conversion as conversion
import requests
import uuid

# api router instance to use with fastapi server
router = APIRouter()

@router.get('/taxii2/{api_root}/collections/', tags=['Collections'])
def get_misp_collections(request: Request = None, response: Response = None):
    """
    fetch all misp tags and convert them into taxii 2.1 collections.
    each tag becomes a collection.
    """
    # extract headers from initial request
    headers = dict(request.headers)
    print(headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    try:
        misp_response = misp.query_misp_api('/tags/index', headers=headers)
        tags = misp_response.get('Tag')  #returns a list of tag dicts
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            raise HTTPException(status_code=403, detail='The client does not have access to this collection resource')

    # determine user permissions from misp
    print('getting user perms...')
    can_write,_=misp.get_user_perms(headers=headers) #function to check write access
    
    # convert each misp tag into taxii collection object
    collections = []
    for tag in tags:
        collections.append({
            'id': conversion.str_to_uuid(tag['id']), #convert id to uuid, taxii requires uuid
            'title': tag['name'],
            'description': tag.get('description', None),
            'can_read': True, #if user got this far through request, can access
            'can_write': can_write,
            'media_types': ['application/taxii+json;version=2.1'] #NOT SURE IF THIS SHOULD BE SET
        })
        
    # set taxii content type in header as per specs
    response.headers['Content-Type']= 'application/taxii+json;version=2.1'
    
    # return in format defined by specs
    return {'collections':collections}

@router.get('/taxii2/{api_root}/collections/{collection_uuid}', tags=['Collections'])
def get_misp_collection(collection_uuid: str, request: Request, response: Response):
    """
    since taxii requires uuid and misp id, need to fetch all tags and filter in code, cannot query for id
    """
    # extract headers from initial request
    headers = dict(request.headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    try:
        misp_response = misp.query_misp_api('/tags/index', headers=headers)
        tags = misp_response.get('Tag')  #returns a list of tag dicts
    except requests.exceptions.HTTPError as e:
        if e.status_code==403:
            raise HTTPException(status_code=403, detail='The client does not have access to this collection resource')

    # determine user permissions from misp
    print('getting user perms...')
    can_write,_=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    # find matching tag, converting each collection id to uuid then checking if match
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='The Collection ID is not found') #error if no matching tag
    
    response.headers['Content-Type']= 'application/taxii+json;version=2.1'
    
    return {
        'id': conversion.str_to_uuid(tag['id']), #convert id to uuid
        'title': tag['name'],
        'description': tag.get('description', None),
        'can_read': True, #if user got this far through request, can access
        'can_write': can_write,
        'media_types': ['application/taxii+json;version=2.1'] #NOT SURE IF THIS SHOULD BE SET
    }