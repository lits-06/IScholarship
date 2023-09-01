from fastapi import FastAPI

from .db.mongo import connect_to_mongo

db = connect_to_mongo()

app = FastAPI()

app.include_router(login.router, prefix="/api")

@app.get("/")
def read_root():
    return {"Hello": "World"}


