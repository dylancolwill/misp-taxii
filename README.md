# misp-taxii

## Description

This project provides a TAXII 2.1 API interface for MISP, allowing clients to interact with MISP data using TAXII endpoints.

## Features

## Install
Download the latest repository and create a virtual environment
```
git clone https://github.com/dylancolwill/misp-taxii.git
cd misp-taxii
python -m venv venv
.\venv\Scripts\activate (Windows)
source ./venv/bin/activate (Linux/macOS)
```

To install all the necessary libraries for this project
```
pip install -r requirements.txt
```

## Usage
By default, the server runs on localhost at port 8000. This can be configured inside `main.py`, see the [FasiAPI server deployment docs](https://fastapi.tiangolo.com/deployment/manually/#run-the-server-program), or additionally, [running behind a proxy](https://fastapi.tiangolo.com/ja/advanced/behind-a-proxy/).


TAXII API roots must be configured before starting the server, this can be set in `endpoints/root.py`.


To start the server, run `main.py`
```
python main.py
```


Begin by sending a request to the discovery endpoint with required headers
```
curl -X GET "http://127.0.0.1:8000/taxii2/" \
  -H "Authorization: <YOUR_API_KEY>" \
  -H "Accept: application/taxii+json;version=2.1" \
  -H "Content-Type: application/taxii+json;version=2.1"
```
or check `tests/discovery_test.py` for Python example. To run tests, MISP auth key is required to be set in `creds.py`.



Additionally, open `demo/index.html` for a visual interaction and set MISP auth key in `demo/script.js` and update endpoints accordingly, not required but is easier for testing.
