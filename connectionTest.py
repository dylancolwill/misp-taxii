import urllib3
from pymisp import PyMISP

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

misp = PyMISP("https://localhost:8443", "61jDTaLYkKuPdNGc9DATaEa6DyM5N3Sf5CynNTl6", False)
events = misp.search(limit=5)
print(events)


from misp_stix_converter import misp_to_stix2
stix_package = misp_to_stix2.convert_event(misp.search(controller='events', limit=1))