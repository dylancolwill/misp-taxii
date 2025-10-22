### **get\_misp\_collection**

*File Location***:** endpoints/collections.py

*Endpoint***:**   
GET /taxii2/{api\_root}/collections/{collection\_uuid}/

*The goal of this endpoint is to retrieve information about a specific TAXII collection.*

*Each MISP tag is treated as a TAXII collection object.*

*Description*  
This endpoint provides general information about a single TAXII Collection. Used by clients to understand the collection’s name, description, and user access permissions before requesting or pushing data.

The endpoint queries MISP for all tags, matches the provided collection\_uuid against each converted tag ID, and returns the matching tag.

*Example Request*  
GET http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/

Authorization: \<misp-api-key\>  
Accept: application/taxii+json;version=2.1  
Content-Type: application/taxii+json;version=2.1

| Parameters |  |  |
| ----- | :---- | :---- |
| ***Name*** | ***Type*** | ***Use*** |
| *api\_root* | *str* | The identifier of the TAXII API root. |
| *collection\_uuid* | *str* | UUID of desired TAXII collection, derived from MISP tag id. |
| **Raises** |  |  |
| ***Code*** | ***Description*** |  |
| *400* | The server did not understand the request or parameters. |  |
| *401* | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |  |
| *403* | The client does not have access to this collections resource. |  |
| *404* | The API Root or Collection ID are not found |  |
| *406* | Unsupported media type in Accept header. |  |
| **Returns** |  |  |
| ***Code*** | ***Body*** | ***Description*** |
| *200* | *{id, title, description, can\_read, can\_write, media\_types}* | Returns metadata describing the specified collection. |
| **Logic** |  |  |
| Get all MISP tags. Get all MISP tags, convert each tag name to uuid and compare with collection\_uuid to find MISP tag. Build response using metadata sourced from match.  Return the envelope response and set TAXII response headers. |  |  |