from fastapi import FastAPI
import uvicorn

# import routers
from endpoints.discovery import router as discovery_router
from endpoints.collections import router as collections_router
from endpoints.objects import router as objects_router

# init fast api
app = FastAPI(
    title="MISP TAXII Server",
)

# register endpoints
app.include_router(discovery_router)
app.include_router(collections_router)
app.include_router(objects_router)

# start the server when file is run
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
 