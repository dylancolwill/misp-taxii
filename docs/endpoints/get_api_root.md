### **get\_api\_root**

**File Location:** `endpoints/root.py`

**Endpoint:**  
`GET /taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/versions/`

*The goal of this endpoint is to provide metadata about the TAXII server, including available API Roots. This allows clients to discover what data and services the server exposes.*

**Description**  
This endpoint returns general information about the TAXII server, including its title, description, and the API Roots. Clients can use this as the entry point to explore the server’s available data.

The API roots are dynamically generated from the server configuration. Access is permission based, clients will only see API Roots if they have access.

MISP does not have native support for roots equivalent, instead associated with different MISP servers. The MISP IP is defined through API roots and is used in each request.

**Example Request**  
```
GET http://127.0.0.1:8000/taxii2/

Authorization: <misp-api-key>
Accept: application/taxii+json;version=2.1
Content-Type: application/taxii+json;version=2.1
```

#### Parameters

| Name      | Type | Use                                    |
|-----------|------|----------------------------------------|
| api_root  | str  | The identifier of the TAXII API root.  |

#### Raises

| Code | Description                                                                                   |
|------|----------------------------------------------------------------------------------------------|
| 401  | The client needs to authenticate. Incorrect header formatting or missing Authorization field. |
| 403  | The client does not have access to this API root.                                             |
| 404  | The requested API root does not exist.                                                        |
| 406  | Unsupported media type in Accept header.                                                      |

#### Returns

| Code | Body                                                                 | Description                                                                 |
|------|----------------------------------------------------------------------|-----------------------------------------------------------------------------|
| 200  | {title: str, description: str, versions: str, max_content_length: int} | Returns a TAXII discovery object containing metadata about the server and its advertised API Roots. |

#### Logic

| Step |
|------|
| Authenticate the client using request headers. Check whether the specified API root exists in the static dictionary. Return the root information with