from fastapi import APIRouter, HTTPException, status
from math import ceil
from bson import ObjectId

from ..db.mongo import db


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


# @router.post("/recommendation")
# async def recommendation(user_id: str):
#     code something...
