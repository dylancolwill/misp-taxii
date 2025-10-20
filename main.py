from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# import routers
from endpoints.discovery import router as discovery_router
from endpoints.collections import router as collections_router
from endpoints.objects import router as objects_router
from endpoints.manifests import router as manifests_router
from endpoints.root import router as root_router

# init fast api
app = FastAPI(
    title="MISP TAXII Server",
)

# init logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)

# cors
# FOR DEMO, MAY NEED TO CHANGE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"], 
)

# register endpoints
app.include_router(discovery_router)
app.include_router(collections_router)
app.include_router(objects_router)
app.include_router(manifests_router)
app.include_router(root_router)

# start the server when file is run
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 