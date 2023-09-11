from fastapi import FastAPI

from .db.mongo import connect_to_mongo
from .router import login

db = connect_to_mongo()

app = FastAPI()

app.include_router(user.router, prefix="/api")

@app.get("/")
def read_root():
    return {"Hello": "World"}


