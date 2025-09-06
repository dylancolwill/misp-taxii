from misp_stix_converter import MISPtoSTIX21Parser

def mispToStix(event):
    # takes misp event converts to json
    parser21 = MISPtoSTIX21Parser()
    parser21.parse_misp_event(event)
    return parser21.bundle

def jsonToStix(json):
    pass