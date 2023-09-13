from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Request
from bson import ObjectId

from app.router.deps import get_user_id
from ..db.mongo import db

router = APIRouter()
achievement_collection = db["achievement"]


@router.post("/create_achievement")
async def create_achievement(request: Request, achievement: dict = Body(...)):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    achievement_collection.insert_one({"user_id": user_id, **achievement})
    return "Tạo thành tích thành công"


@router.get("/get_all_achievement")
async def get_all_achievement(request: Request):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    projection = {"_id": False, "title": True, "role": True, "description": True}
    cursor = achievement_collection.find({"user_id": user_id}, projection)
    achievement_list = list(cursor)
    return {"data": achievement_list}
    

@router.put("/update_achievement")
async def update_achievement(request: Request, update: dict = Body(...)):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    achievement_id = ObjectId(update.pop("achievement_id"))
    query = {"_id": achievement_id, "user_id": user_id}
    existing_achievement = achievement_collection.find_one(query)
    if existing_achievement is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy thành tích")
    achievement_collection.update_one({"_id": achievement_id, "user_id": user_id}, {"$set": update})
    return "Cập nhật thành công"
    

@router.delete("/delete_achievement")
async def delete_achievement(request: Request, achievement_id: str):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    query = {"_id": ObjectId(achievement_id), "user_id": user_id}
    existing_achievement = achievement_collection.find_one(query)
    if existing_achievement:
        achievement_collection.delete_one(query)
        return "Xóa thành tích thành công"
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy bài viết")


