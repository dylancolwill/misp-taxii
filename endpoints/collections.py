from fastapi import APIRouter, Depends, Request, HTTPException, Response
import functions.misp as misp
import functions.conversion as conversion
import requests
import uuid

# api router instance to use with fastapi server
router = APIRouter()

@router.get('/taxii2/{api_root}/collections/', tags=['Collections'])
def get_misp_collections(request: Request = None, response: Response = None):

    """Fetch all misp tags and convert them into taxii 2.1 collections.
    NOTE: Each tag becomes a collection.

    Parameters:
        request:
        reponse:

    Returns:
        TAXII Collections: Returns ALL TAXII Collections, they contain an ID, Title, Description, Read and Write Permissions
    """    
    # extract headers from initial request
    headers = dict(request.headers)
    print(headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    misp_response = misp.query_misp_api('/tags/index', headers=headers)
    tags = misp_response.get('Tag')  #returns a list of tag dicts

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
    Since taxii requires uuid and misp id, need to fetch all tags and filter in code, cannot query for id
    
    Parameters:
        collection_uuid: Created by converting Tag ID. Allows for Tag-Collection Mapping
        request:
        response:
    
    Raises:
        404: Returns if no matching Tag is found

    Returns:
        TAXII Collection: Containing an ID, Title, Description, Read and Write Permissions
    """    
    # extract headers from initial request
    headers = dict(request.headers)
    
    # query misp for all tags using headers
    print('getting all misp tags...')
    misp_response = misp.query_misp_api('/tags/index', headers=headers)
    tags = misp_response.get('Tag')  #returns a list of tag dicts

    # determine user permissions from misp
    print('getting user perms...')
    can_write,_=misp.get_user_perms(headers=headers) #get the user perms from function in core
    
    # find matching tag, converting each collection id to uuid then checking if match
    print('comparing each tag id to user inputted uuid...')
    tag = next((t for t in tags if conversion.str_to_uuid(str(t['id'])) == collection_uuid), None)
    if not tag:
        raise HTTPException(status_code=404, detail='Collection not found') #error if no matching tag
    
    response.headers['Content-Type']= 'application/taxii+json;version=2.1'
    
    return {
        'id': conversion.str_to_uuid(tag['id']), #convert id to uuid
        'title': tag['name'],
        'description': tag.get('description', None),
        'can_read': True, #if user got this far through request, can access
        'can_write': can_write,
        'media_types': ['application/taxii+json;version=2.1'] #NOT SURE IF THIS SHOULD BE SET
    }