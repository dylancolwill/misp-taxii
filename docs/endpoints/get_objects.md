### **get\_objects**

*File Location***:** endpoints/[objects.py](http://objects.py)

*Endpoint***:**   
GET /taxii2/{api\_root}/collections/{collection\_uuid}/objects/

*The goal of this endpoint is to retrieve multiple STIX objects from a specific TAXII collection.*

*Description*  
This endpoint retrieves all STIX objects available in a given TAXII collection. Internally, it maps the TAXII collection UUID to the corresponding MISP tag, fetches all related MISP events, converts them into STIX objects, and aggregates the results into a TAXII envelope. The endpoint supports filtering, allowing clients to search for objects by type, ID, version, or creation time. Pagination is also supported using the limit and next parameters for large result sets.

*Example Request*  
GET http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90  
/objects/

Authorization: \<misp-api-key\>  
Accept: application/taxii+json;version=2.1  
Content-Type: application/taxii+json;version=2.1

| Parameters |  |  |
| ----- | :---- | :---- |
| ***Name*** | ***Type*** | ***Use*** |
| *api\_root* | *str* | The identifier of the TAXII API root. |
| *collection\_uuid* | *str* | UUID of desired TAXII collection, derived from MISP tag id. Included in API request URL.  |
| *added\_after* | *str, optional* | Retrieve objects created after a certain date. e.g., ?added\_after=2017-10-21T11:34:57+00:00 |
| *limit* | *int, optional* | Defines the number of objects to return, must be positive e.g., ?limit=2 |
| *next* | *str, optional* | Pagination token used to retrieve subsequent results. e.g., ?next=2 |
| *id* | *str, optional* | Filter by a specific STIX object ID. e.g., ?match\[id\]=report--59e9ec59-a888-48e4-afb4-441602de0b81 |
| *type* | *str, optional* | Filter by STIX object type e.g., ?match\[id\]=report |
| *version* | *str, optional* | Version of the object. e.g., ?match\[version\]=2017-10-21T11:34:57+00:00 |
| *spec\_version* | *str, optional* | Filter by STIX specification version. e.g., ?match\[spec\_version\]=2.1 |
| **Raises** |  |  |
| ***Code*** | ***Description*** |  |
| *400* | The server did not understand the request or filter parameters. Usually non-positive integer has been used as the 'limit' parameter, ‘or added\_after parameter was not an ISO date string |  |
| *401* | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |  |
| *403* | The client does not have access to this object resource. |  |
| *404* | The API Root or Collection ID are not found |  |
| *406* | Unsupported media type in Accept header. |  |
| **Returns** |  |  |
| ***Code*** | ***Body*** | ***Description*** |
| *200* | *{objects:\[objects\]}* | Returns a TAXII envelope containing the requested STIX objects. |
| **Logic** |  |  |
| Get all MISP tags, convert each tag name to uuid and compare with collection\_uuid to find MISP tag. Query MISP for events that have that tag and apply built in MISP filters.  Convert the returned MISP events into STIX objects and flatten them into a single list. Apply any client filters not included in MISP to that list, including finding the specific object via UUID. Slice the filtered list according to limit and next to produce the current page. Build the envelope response and set TAXII response headers. |  |  |