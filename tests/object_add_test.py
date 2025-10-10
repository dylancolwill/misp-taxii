import requests
import pprint
import creds

url = "http://127.0.0.1:8000/taxii2/api1/collections/f37b15ee-07ba-583f-bf65-03e4fd5e9d96/objects/"
headers = {
    "Authorization": creds.get_creds(),
    "Accept": "application/taxii+json;version=2.1",
    "Content-Type": "application/taxii+json;version=2.1"
}

stix_bundle = {
    "type": "bundle",
    "id": "bundle--" + "6b3f5a9c-7c12-4e8d-bf92-2d3f5b1f9a2e",
    "objects": [
        {
            "type": "identity",
            "spec_version": "2.1",
            "id": "identity--" + "f8c4e8b1-1d3a-4a5b-a67d-9f2c8b2d3e1f",
            "created": "2025-10-10T00:00:00.000Z",
            "modified": "2025-10-10T00:00:00.000Z",
            "name": "MISP-Project",
            "identity_class": "organization",
        },
        {
            "type": "grouping",
            "spec_version": "2.1",
            "id": "grouping--" + "d7e9c1f4-4a9b-4e77-8f5a-2b3c9d8e7f1a",
            "created_by_ref": "identity--f8c4e8b1-1d3a-4a5b-a67d-9f2c8b2d3e1f",
            "created": "2025-10-10T00:00:00.000Z",
            "modified": "2025-10-10T00:00:00.000Z",
            "name": "MISP-STIX-Converter test event",
            "context": "suspicious-activity",
            "object_refs": ["indicator--a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d"],
            "labels": ["Threat-Report", 'misp:tool="MISP-STIX-Converter"'],
        },
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--" + "a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
            "created_by_ref": "identity--f8c4e8b1-1d3a-4a5b-a67d-9f2c8b2d3e1f",
            "created": "2025-10-10T00:00:00.000Z",
            "modified": "2025-10-10T00:00:00.000Z",
            "pattern": "[autonomous-system:number = '174']",
            "pattern_type": "stix",
            "pattern_version": "2.1",
            "valid_from": "2025-10-10T00:00:00Z",
            "kill_chain_phases": [
                {"kill_chain_name": "misp-category", "phase_name": "Network activity"}
            ],
            "labels": [
                'misp:type="AS"',
                'misp:category="Network activity"',
                'misp:to_ids="True"',
            ],
        },
    ],
}


resp = requests.post(url, headers=headers, json=stix_bundle)
print("Status:", resp.status_code)
pprint.pp(resp.json())