import uuid

def str_to_uuid(string):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, str(string)))