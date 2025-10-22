### **get\_misp\_collections**

*File Location***:** endpoints/collections.py

*Endpoint***:**   
GET /taxii2/{api\_root}/collections/

*The goal of this endpoint is to retrieve all TAXII collections.*

*Each MISP tag is treated as a TAXII collection object.*

*Description*  
Retrieves all MISP tags accessible to the authenticated user and converts each into a TAXII collection.

Each collection includes an ID (UUID of the MISP tag ID), title, description, and access permissions.

*Example Request*  
GET http://127.0.0.1:8000/taxii2/api1/collections/

Authorization: \<misp-api-key\>  
Accept: application/taxii+json;version=2.1  
Content-Type: application/taxii+json;version=2.1

| Parameters |  |  |
| ----- | :---- | :---- |
| ***Name*** | ***Type*** | ***Use*** |
| *api\_root* | *str* | The identifier of the TAXII API root. |
| **Raises** |  |  |
| ***Code*** | ***Description*** |  |
| *400* | The server did not understand the request or parameters. |  |
| *401* | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |  |
| *403* | The client does not have access to this collections resource. |  |
| *404* | The API Root or Collection ID are not found |  |
| *406* | Unsupported media type in Accept header. |  |
| **Returns** |  |  |
| ***Code*** | ***Body*** | ***Description*** |
| *200* | *{collections:\[collections\]}* | Returns a TAXII envelope containing a list of collections. |
| **Logic** |  |  |
| Get all MISP tags. Build response using metadata sourced from list.  Return the envelope response and set TAXII response headers. |  |  |