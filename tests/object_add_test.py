import requests
import pprint
import creds
import uuid

url = "http://127.0.0.1:8000/taxii2/api1/collections/f37b15ee-07ba-583f-bf65-03e4fd5e9d96/objects/"
headers = {
    "Authorization": creds.get_creds(),
    "Accept": "application/taxii+json;version=2.1",
    "Content-Type": "application/taxii+json;version=2.1"
}

identity_uuid = str(uuid.uuid4())
grouping_uuid = str(uuid.uuid4())
indicator_uuid = str(uuid.uuid4())
bundle_uuid = str(uuid.uuid4())

stix_bundle = {
    "type": "bundle",
    "id": f"bundle--{bundle_uuid}",
    "objects": [
        {
            "type": "identity",
            "spec_version": "2.1",
            "id": f"identity--{identity_uuid}",
            "created": "2025-10-10T00:00:00.000Z",
            "modified": "2025-10-10T00:00:00.000Z",
            "name": "MISP-Project",
            "identity_class": "organization",
        },
        {
            "type": "grouping",
            "spec_version": "2.1",
            "id": f"grouping--{grouping_uuid}",
            "created_by_ref": f"identity--{identity_uuid}",
            "created": "2025-10-10T00:00:00.000Z",
            "modified": "2025-10-10T00:00:00.000Z",
            "name": "MISP-STIX-Converter test event",
            "context": "suspicious-activity",
            "object_refs": [f"indicator--{indicator_uuid}"],
            "labels": ["Threat-Report", 'misp:tool="MISP-STIX-Converter"'],
        },
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{indicator_uuid}",
            "created_by_ref": f"identity--{identity_uuid}",
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