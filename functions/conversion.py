from misp_stix_converter import MISPtoSTIX21Parser

def misp_to_stix(event):
    # takes misp event converts to json
    parser21 = MISPtoSTIX21Parser()
    parser21.parse_misp_event(event)
    return parser21.bundle

def json_to_stix(json):
    pass