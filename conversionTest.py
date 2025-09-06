import functions.misp as misp
import functions.conversion as conversion

mispObject = misp.connect()
# print(misp.search(controller='events', limit=1)[0])
# print(misp.get_stix(event_id=1))

# print(mispConversion.stix(misp.search(controller='events', limit=1)))

json =misp.getMispEventsApi()
print(mispObject.search(controller='events', limit=1)[0])
print(json[0])
# print(conversion.eventToStix(json[0]))

# print(conversion.eventToStix(mispObject.search(controller='events', limit=1)[0]))
