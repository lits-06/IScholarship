from fastapi import FastAPI

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:admin123@cluster0.ymqhm3k.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["db"]

collection_scholarship = db["scholarship"]

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users")
def create_user(name: str | None = None, age: int | None = None):
    if name and age:
        collection_scholarship.insert_one({"name": name, "age": age})
        return "Update success"
    return "Lack of infomation"

@app.get("/all")
def all_user():
    projection = {"_id": False}
    documents = list(collection_scholarship.find({}, projection))
    return {"users": documents}


