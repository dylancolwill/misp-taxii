# misp-taxii

## todo
- [x] function in misp.py to check user perms, will need for can_write and can_read collections
- [ ] verify responses follow spec
  - [x] discovery endpoint
  - [x] collections endpoint
  - [x] manifests endpoint
  - [ ] objects
  - [x] api root
- [ ] https to securely use api keys, enable tls verification
- [x] verify user passes api key
- [x] include manifests filtering
- [x] map misp events to stix object type to include in uuid for taxii objects
- [ ] make use of api roots
- [ ] remove testing and development code blocks
- [ ] test filters