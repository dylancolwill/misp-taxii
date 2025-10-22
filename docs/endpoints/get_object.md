### **get\_object**

**File Location:** `endpoints/objects.py`

**Endpoint:**  
`GET /taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/`

*The goal of this endpoint is to retrieve a specific object.*

**Description**  
This endpoint fetches a single STIX object by its UUID from a specified TAXII collection. Internally, it maps the TAXII collection UUID to a MISP tag, retrieves related MISP events, converts them into STIX objects, and filters to return the object matching the supplied object\_uuid. Optional query parameters allow further filtering.

**Example Request**  
```
GET http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/objects/report--59e9ec59-a888-48e4-afb4-441602de0b81

Authorization: <misp-api-key>
Accept: application/taxii+json;version=2.1
Content-Type: application/taxii+json;version=2.1
```

#### Parameters

| Name            | Type           | Use                                                                                      |
|-----------------|----------------|-----------------------------------------------------------------------------------------|
| api_root        | str            | The identifier of the TAXII API root.                                                   |
| collection_uuid | str            | UUID of desired TAXII collection, derived from MISP tag id. Included in API request URL.|
| object_uuid     | str            | UUID of desired TAXII object. Included in API request URL.                              |
| added_after     | str, optional  | Retrieve objects created after a certain date. e.g., `?added_after=2017-10-21T11:34:57+00:00` |
| limit           | int, optional  | Defines the number of objects to return, must be positive e.g., `?limit=2`              |
| next            | str, optional  | Pagination token used to retrieve subsequent results. e.g., `?next=2`                   |
| version         | str, optional  | Version of the object. e.g., `?match[version]=2017-10-21T11:34:57+00:00`                |
| spec_version    | str, optional  | Filter by STIX specification version. e.g., `?match[spec_version]=2.1`                  |

#### Raises

| Code | Description                                                                                   |
|------|----------------------------------------------------------------------------------------------|
| 400  | The server did not understand the request or filter parameters. Usually non-positive integer has been used as the 'limit' parameter, or added_after parameter was not an ISO date string. |
| 401  | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |
| 403  | The client does not have access to this object resource. MISP denying access.                 |
| 404  | The API Root or Collection ID are not found                                                   |
| 406  | Unsupported media type in Accept header.                                                      |

#### Returns

| Code | Body                | Description                                                            |
|------|---------------------|------------------------------------------------------------------------|
| 200  | {objects:[object]}  | Returns a TAXII envelope containing the requested STIX object.          |

#### Logic

| Step |
|------|
| 1. Get all MISP tags, convert each tag name to uuid and compare with collection_uuid to find MISP tag.<br>2. Query MISP for events that have that tag and apply built-in MISP filters.<br>3. Convert the returned MISP events into STIX objects and flatten them into a single list.<br>4. Apply any client filters not included in MISP to that list, including finding the specific object via UUID.<br>5. Slice the filtered list according to limit and next to produce the current page.<br>6. Build the envelope response and set TAXII