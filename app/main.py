from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.api import api_router

app = FastAPI()
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def check_healthy():
    return {"200": "OK"}
