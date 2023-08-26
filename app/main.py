from fastapi import FastAPI
from pymongo import MongoClient

client = MongoClient("mongodb://team1:123@mongodb:27017/")

db = client["db"]

scholarship = db["member"]

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users")
def create_user(name: str | None = None, age: int | None = None):
    if name and age:
        scholarship.insert_one({"name": name, "age": age})
        return "Update success"
    return "Lack of infomation"

@app.get("/all")
def all_user():
    projection = {"_id": False}
    documents = list(scholarship.find({}, projection))
    return {"users": documents}


