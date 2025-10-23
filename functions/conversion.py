from fastapi import HTTPException
from misp_stix_converter import MISPtoSTIX21Parser, InternalSTIX2toMISPParser
from stix2 import parse
import uuid
#File to help with STIX conversion, w/o having to repeat the function in multiple files

# convert string to uuid. needed for taxii collections, using misp tag names as seed
# taxii specs requires uuid4 but there is no way to convert string deterministically
# uuid v4 and v5 have the same output format
def str_to_uuid(string):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, str(string)))

def misp_to_stix(event):
    # takes misp event converts to json
    parser21 = MISPtoSTIX21Parser()
    parser21.parse_misp_event(event)
    return parser21.bundle

def stix_to_misp(bundle):
    # function to convert stix back to misp
    try:
        parser = InternalSTIX2toMISPParser()
        parser.load_stix_bundle(bundle)
        parser.parse_stix_bundle()
        return parser.misp_events
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to convert STIX to MISP {e}')

def datetime_to_iso(dt):
    # convert datetime into iso
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)