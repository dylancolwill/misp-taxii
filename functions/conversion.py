from misp_stix_converter import MISPtoSTIX21Parser
from stix2 import parse
import uuid
#File to help with STIX conversion, w/o having to repeat the function in multiple files

def str_to_uuid(string):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, str(string)))


def misp_to_stix(event):
    # takes misp event converts to json
    parser21 = MISPtoSTIX21Parser()
    parser21.parse_misp_event(event)
    return parser21.bundle

def json_to_stix(json):
    obj = parse(json)
    print(obj)
