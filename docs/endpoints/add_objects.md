### **add\_objects**

*File Location***:** endpoints/objects.py

*Endpoint***:**   
GET /taxii2/{api\_root}/collections/{collection\_uuid}/objects/

*The goal of this endpoint is to add a STIX object to a specific TAXII collection.* 

*Description*  
Allows clients to publish new STIX objects into a TAXII Collection. All submitted objects must be wrapped in a TAXII envelope. The server validates authentication, permissions, and payload format before processing. If the collection’s can\_write property is set to false for the client, the request is rejected.

If accepted, the endpoint returns a status resource describing whether the submitted objects were successfully processed, are still pending, or failed. Duplicate objects are not permitted. 

*Example Request*  
POST http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/

Authorization: \<misp-api-key\>  
Accept: application/taxii+json;version=2.1  
Content-Type: application/taxii+json;version=2.1

{objects:\[object\]}

| Parameters |  |  |
| ----- | :---- | :---- |
| ***Name*** | ***Type*** | ***Use*** |
| *api\_root* | *str* | The identifier of the TAXII API root. |
| *collection\_uuid* | *str* | UUID of desired TAXII collection, derived from MISP tag id. Included in API request URL.  |
| **Raises** |  |  |
| ***Code*** | ***Description*** |  |
| *400* | The server did not understand the request. Invalid JSON or TAXII envelope.  |  |
| *401* | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |  |
| *403* | The client does not have access to write to this collection resource. |  |
| *404* | The API Root or Collection ID are not found |  |
| *406* | Unsupported media type in Accept header. |  |
| *413* | The payload exceeds the maximum allowed size. |  |
| *415* | The Content-Type is unsupported. |  |
| *422* | The object type, version, or format cannot be processed. |  |
| **Returns** |  |  |
| ***Code*** | ***Body*** | ***Description*** |
| *202* | *{status\_resource}* | Request has been accepted. Returns a status resource describing the result. |
| **Logic** |  |  |
| Get all MISP tags, convert each tag name to uuid and compare with collection\_uuid to find MISP tag. Parse the TAXII envelope and validate the structure of the contained STIX objects. Push to the collection, if duplicate will deny. Apply any client filters not included in MISP to that list, including finding the specific object via UUID. Generate a status resource with successful, pending, and failed submissions. Return response and set TAXII response headers. |  |  |