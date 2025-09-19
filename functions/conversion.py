import uuid

def str_to_uuid(string):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, str(string)))

from misp_stix_converter import MISPtoSTIX21Parser
from stix2 import parse

def misp_to_stix(event):
    # takes misp event converts to json
    parser21 = MISPtoSTIX21Parser()
    parser21.parse_misp_event(event)
    return parser21.bundle

def json_to_stix(json):
    obj = parse(json)
    print(obj)