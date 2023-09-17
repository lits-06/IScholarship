from fastapi import APIRouter, HTTPException, status, Request
from math import ceil
from bson import ObjectId
import re

from db.mongo import db
from router.deps import get_user_id


router = APIRouter()
user_collection = db["user"]
scholarship_collection = db["scholarship"]
scholarshipuser_collection = db["scholarshipuser"]

@router.get("/get_all_model")
async def get_all_model():
    cursor_user = user_collection.find()
    user = [user_doc | {"_id": str(user_doc["_id"])} for user_doc in cursor_user]

    cursor_scholarship = scholarship_collection.find()
    scholarship = [scholarship_doc | {"_id": str(scholarship_doc["_id"])} for scholarship_doc in cursor_scholarship]

    cursor_scholarshipuser = scholarshipuser_collection.find()
    scholarshipuser = [scholarshipuser_doc | {"_id": str(scholarshipuser_doc["_id"])} for scholarshipuser_doc in cursor_scholarshipuser]
    
    return {"user": user, "scholarship": scholarship, "scholarshipuser": scholarshipuser}


@router.post("/get_recommendation")
async def get_recommendation(data: dict):
    query = {}
    if "type" in data:
        query["type"] = data["type"]
    if "education_level" in data:
        regex_pattern = re.compile(fr".*{data['education_level']}.*")
        query["education_level"] = {"$regex": regex_pattern}
    if "major" in data:
        regex_pattern = re.compile(fr".*{data['major']}.*")
        query["major"] = {"$regex": regex_pattern}
    cursor = scholarship_collection.find(query).skip(0).limit(10)
    result = [record | {"_id": str(record["_id"])} for record in cursor]
    return result
    

# @router.post("/auto_recommendation")
# async def auto_recommendation(user_id: str)
#     code sth here...
    
