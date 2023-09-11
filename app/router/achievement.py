from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId

from ..db.mongo import db

router = APIRouter()
achievement_collection = db["achievement"]


@router.post("/create_achievement", tags = ["achievement"])
async def create_achievement(user_id: str, achievement: Annotated[dict, Body(...)]):
    achievement_collection.insert_one({"user_id": user_id, **achievement.dict()})
    return "Tạo thành tích thành công"


@router.get("/get_all_achievement", tags = ["achievement"])
async def get_all_achievement(user_id: str):
    projection = {"title": True, "role": True, "description": True}
    cursor = achievement_collection.find({"user_id": user_id}, projection)
    achievement_list = list(cursor)
    return {"data": achievement_list}
    

@router.put("/update_achievement", tags = ["achievement"])
async def update_achievement(user_id: str, update: Annotated[dict, Body(...)]):
    query = {"_id": ObjectId(update["_id"]), "user_id": user_id}
    existing_achievement = achievement_collection.find_one(query)
    if existing_achievement is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy thành tích")
    achievement_collection.update_one({"_id": ObjectId(update["_id"]), "user_id": user_id}, {"$set": update})
    

@router.delete("/delete_achievement", tags = ["achievement"])
async def delete_achievement(user_id: str, achievement_id: str):
    query = {"_id": ObjectId(achievement_id), "user_id": user_id}
    existing_achievement = achievement_collection.find_one(query)
    if existing_achievement:
        achievement_collection.delete_one(query)
        return "Xóa thành tích thành công"
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy bài viết")


