from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId

from ..db.mongo import db

router = APIRouter()
achievement_collection = db["achievement"]


@router.post("/create_achievement")
async def create_achievement(user_id: str, achievement: dict = Body(...)):
    achievement_collection.insert_one({"user_id": user_id, **achievement})
    return "Tạo thành tích thành công"


@router.get("/get_all_achievement")
async def get_all_achievement(user_id: str):
    projection = {"_id": False, "title": True, "role": True, "description": True}
    cursor = achievement_collection.find({"user_id": user_id}, projection)
    achievement_list = list(cursor)
    return {"data": achievement_list}
    

@router.put("/update_achievement")
async def update_achievement(user_id: str, update: dict = Body(...)):
    achievement_id = ObjectId(update.pop("achievement_id"))
    query = {"_id": achievement_id, "user_id": user_id}
    existing_achievement = achievement_collection.find_one(query)
    if existing_achievement is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy thành tích")
    achievement_collection.update_one({"_id": achievement_id, "user_id": user_id}, {"$set": update})
    return "Cập nhật thành công"
    

@router.delete("/delete_achievement")
async def delete_achievement(user_id: str, achievement_id: str):
    query = {"_id": ObjectId(achievement_id), "user_id": user_id}
    existing_achievement = achievement_collection.find_one(query)
    if existing_achievement:
        achievement_collection.delete_one(query)
        return "Xóa thành tích thành công"
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy bài viết")


