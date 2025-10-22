### **get\_manifests**

**File Location:** `endpoints/manifests.py`

**Endpoint:**  
`GET /taxii2/{api_root}/collections/{collection_uuid}/manifests`

*The goal of this endpoint is to return manifest entries for objects in a TAXII collection.*

**Description**  
This endpoint returns manifest entries for all STIX objects in a given TAXII collection. Clients can use this to discover available objects, their versions, and their metadata before requesting the full objects.

Supports filtering by object ID, type, version, and pagination via `limit` and `next`.

**Example Request**  
```
GET http://127.0.0.1:8000/taxii2/api1/collections/28dfa8c5-dff4-52ad-90df-e5112b2ade90/manifests

Authorization: <misp-api-key>
Accept: application/taxii+json;version=2.1
Content-Type: application/taxii+json;version=2.1
```

#### Parameters

| Name            | Type           | Use                                                                                      |
|-----------------|----------------|-----------------------------------------------------------------------------------------|
| api_root        | str            | The identifier of the TAXII API root.                                                   |
| collection_uuid | str            | UUID of desired TAXII collection, derived from MISP tag id. Included in API request URL.|
| added_after     | str, optional  | Retrieve objects created after a certain date. e.g., `?added_after=2017-10-21T11:34:57+00:00` |
| limit           | int, optional  | Defines the number of objects to return, must be positive e.g., `?limit=2`              |
| next            | str, optional  | Pagination token used to retrieve subsequent results. e.g., `?next=2`                   |
| id              | str, optional  | Filter by a specific STIX object ID. e.g., `?match[id]=report--59e9ec59-a888-48e4-afb4-441602de0b81` |
| type            | str, optional  | Filter by STIX object type e.g., `?match[type]=report`                                  |
| version         | str, optional  | Version of the object. e.g., `?match[version]=2017-10-21T11:34:57+00:00`                |

#### Raises

| Code | Description                                                                                   |
|------|----------------------------------------------------------------------------------------------|
| 400  | The server did not understand the request or filter parameters. Usually non-positive integer has been used as the 'limit' parameter, or added_after parameter was not an ISO date string. |
| 401  | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |
| 403  | The client does not have access to this manifest resource.                                    |
| 404  | The API Root or Collection ID are not found                                                   |
| 406  | Unsupported media type in Accept header.                                                      |

#### Returns

| Code | Body                | Description                                                            |
|------|---------------------|------------------------------------------------------------------------|
| 200  | {objects:[objects]} | Returns a TAXII envelope containing manifest entries for the requested STIX objects. |

#### Logic

| Step |
|------|
| 1. Get all MISP tags, convert each tag name to uuid and compare with collection_uuid to find MISP tag.<br>2. Query MISP for events that have that tag and apply built-in MISP filters.<br>3. Convert the returned MISP events into STIX objects.<br>4. Apply any client filters not included in MISP to that list, including finding the specific object via UUID, type, or version.<br>5. Build manifest entries for each object.<br>6. Slice the filtered list according to limit and next to produce the current page.<br>7. Build the envelope response and set TAXII response