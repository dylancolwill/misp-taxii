# misp-taxii

## Description

This project provides a TAXII 2.1 API interface for MISP, allowing clients to interact with MISP data using TAXII endpoints.

## Features

## Install
Download the latest repository and create a virtual environment
```
git clone https://github.com/dylancolwill/misp-taxii.git && cd misp-taxii
python -m venv venv
./venv/Scripts/activate (Windows)
source ./venv/bin/activate (Linux/macOS)
```

To install all the necessary libraries for this project
```
pip install -r requirements.txt
```

## Usage
To start the server, run `main.py`
```
python main.py
```

By default, the server is run on localhost port 8000
Start by sending a request to the discovery endpoint with required headers
```

```

## To Do
- [x] function in misp.py to check user perms, will need for can_write and can_read collections
- [x] verify responses follow spec
  - [x] discovery endpoint
  - [x] collections endpoint
  - [x] manifests endpoint
  - [x] objects
  - [x] api root
- [ ] https to securely use api keys, enable tls verification
- [x] verify user passes api key
- [x] include filtering
  - [x] test filtering
  - [x] test filtering checks
- [x] map misp events to stix object type to include in uuid for taxii objects
- [x] make use of api roots
- [ ] remove testing and development code blocks
  - [ ] change print statements to debug log
- [x] ensure correct response headers
- [ ] ~~include ability to return taxii and stix~~
- [ ] ability to view headers in demo
- [x] failure responses
  - [ ] test all responses
- [ ] finish install and usage instructions
