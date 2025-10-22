### **get\_discovery**

**File Location:** `endpoints/discovery.py`

**Endpoint:**  
`GET /taxii2/{api_root}/collections/{collection_uuid}/objects/{object_uuid}/versions`

*The goal of this endpoint is to provide metadata about the TAXII server, including available API Roots. This allows clients to discover what data and services the server exposes.*

**Description**  
This endpoint returns general information about the TAXII server, including its title, description, and the API Roots. Clients can use this as the entry point to explore the server’s available data.

The API Roots are dynamically generated from the server configuration. Access is permission based, clients will only see API Roots if they have access.

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
| 403  | The client does not have access to this discovery resource.                                   |
| 406  | Unsupported media type in Accept header.                                                      |

#### Returns

| Code | Body                                   | Description                                                                 |
|------|----------------------------------------|-----------------------------------------------------------------------------|
| 200  | {title: str, description: str, api_roots: [str]} | Returns a TAXII discovery object containing metadata about the server and its advertised API Roots. |

#### Logic

| Step |
|------|
| 1. Authenticate the client using request headers.<br>2. Gather static discovery metadata and dynamically generate the list of API roots from server configuration.<br>3. Return the discovery information with response