from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body
from bson import ObjectId

from app.router.deps import get_user_id
from ..db.mongo import db

router = APIRouter()
scholarshipuser_collection = db["scholarshipuser"]
scholarship_collection = db["scholarship"]


@router.post("/user_save_scholarship")
async def user_save_scholarship(request: Request, scholarship_id: str, data: dict = Body(...)):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    user_scholarship = {
        "user_id": user_id,
        "scholarship_id": scholarship_id,
        **data
    }
    result = scholarshipuser_collection.insert_one(user_scholarship)
    if result.inserted_id:
        return "Đã lưu"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi lưu")
    

@router.post("/user_discard_scholarship")
async def user_discard_scholarship(request: Request, scholarship_id: str, data: dict = Body(...)):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    result = scholarshipuser_collection.update_one(
        {"user_id": user_id, 
        "scholarship_id": scholarship_id},
        {"$set": {**data}}
    )
    if result.modified_count > 0: 
        return "Đã lưu"
    else:
        user_scholarship = {
            "user_id": user_id,
            "scholarship_id": scholarship_id,
            **data
        }
        result = scholarshipuser_collection.insert_one(user_scholarship)
        if result.inserted_id:
            return "Đã lưu"
        else:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi lưu")
        

@router.put("/user_update_saved_scholarship")
async def user_update_saved_scholarship(request: Request, scholarship_id: str, data: dict = Body(...)):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    result = scholarshipuser_collection.update_one(
        {"user_id": user_id, 
        "scholarship_id": scholarship_id},
        {"$set": {**data}}
    )
    if result.modified_count > 0: 
        return "Đã lưu"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Không thể cập nhật dữ liệu")
        

@router.delete("/user_delete_scholarship")
async def user_delete_scholarship(request: Request, scholarship_id: str):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    result = scholarshipuser_collection.delete_one({"user_id": user_id, "scholarship_id": scholarship_id})
    if result.deleted_count > 0:
        return "Xóa thành công"
    else: 
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy dữ liệu để xóa")
    

@router.get("/get_all_shortlist")
async def get_all_shortlist(request: Request):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    projection = {"scholarship_id": True}
    cursor = scholarshipuser_collection.find({"user_id": user_id, "label": 1}, projection)
    scholarship_list = list(cursor)
    if scholarship_list:
        data = []
        for scholarship in scholarship_list:
            id = scholarship["scholarship_id"]
            result = scholarship_collection.find_one({"_id": ObjectId(id)})
            result["_id"] = str(result["_id"])
            data.append(result)
        return {"data": data}
    else:
        return {"data": []}
    


    