### **get\_misp\_manifests**

*File Location***:** endpoints/manifests.py

*Endpoint***:** GET /taxii2/{api\_root}/collections/{collection\_uuid}/manifests

*The goal of this endpoint is to return information about a specific TAXII API Root.*

*Description*  
This endpoint provides general information about a specific TAXII API Root. Each API Root includes a title, description, supported TAXII versions, and the maximum content length allowed.

Clients use this endpoint to determine which API Roots are available and to understand their configurations before requesting collections or objects.

*Example Request*  
GET http://127.0.0.1:8000/taxii2/api1/

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
| ***Code*** | ***Description*** |  |
| *400* | The server did not understand the request or filter parameters. Usually non-positive integer has been used as the 'limit' parameter, ‘or added\_after parameter was not an ISO date string |  |
| *401* | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |  |
| *403* | The client does not have access to this manifest resource.  |  |
| *404* | The API Root or Collection ID are not found |  |
| *406* | Unsupported media type in Accept header. |  |
| **Returns** |  |  |
| ***Code*** | ***Body*** | ***Description*** |
| *200* | *{objects:\[objects\]}* | Returns a TAXII envelope containing metadata for the requested STIX objects. |
| **Logic** |  |  |
| Get all MISP tags, convert each tag name to uuid and compare with collection\_uuid to find MISP tag. Query MISP for events that have that tag and apply built in MISP filters.  Convert the returned MISP events into STIX objects. Apply any client filters not included in MISP to that list, including finding the specific object via UUID. Built manifests entries for each object. Slice the filtered list according to limit and next to produce the current page. Build the envelope response and set TAXII response headers. |  |  |