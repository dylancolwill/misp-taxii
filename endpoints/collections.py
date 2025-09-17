from fastapi import APIRouter, Depends, Request, HTTPException
import functions.misp as misp
import requests

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

    collections = []
    for tag in tags:
        collections.append({
            'id': tag['id'], #using tag name as id, imo best solution
            'title': tag['name'],
            'description': tag.get('description', None),
            'can_read': True, #INCLUDE FUNCTION TO CHECK PERMS FO APIKEY
            'can_write': False,#SAME
            'media_types': ['application/stix+json;version=2.1']
        })
    
    return collections
