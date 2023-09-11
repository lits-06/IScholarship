from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body
from passlib.context import CryptContext

from ..db.mongo import db

router = APIRouter()
user_collection = db["user"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/login-google", tags = ["user"])
async def login_with_google(data: dict):
    email = data["email"]
    existing_user = user_collection.find_one({"email": email})
    if existing_user:
        user_data = {
            "email": existing_user["email"],
            "user_name": existing_user["user_name"]
        }
        return {"user": user_data}
    else:
        new_user = {
            "email": email,
            "user_name": data["user_name"]
        }
        result = user_collection.insert_one(new_user)
        if not result.acknowledged:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm dữ liệu vào cơ sở dữ liệu")
        user_data = {
            "email": data["email"],
            "user_name": data["user_name"]
        }
        return {"user": user_data}


@router.get("/login", tags = ["user"])
async def login(data: dict):
    email = data["email"]
    existing_user = user_collection.find_one({"email": email})
    if not existing_user:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy thông tin người dùng")
    password = existing_user["password"]
    if not pwd_context.verify(data["password"], password):
        raise HTTPException(status_code = 401, detail = "Không xác thực")
    user_data = {
        "email": existing_user["email"],
        "user_name": existing_user["user_name"]
    }
    return {"user": user_data}


@router.post("/register", tags = ["user"])
async def register(data: dict):
    email = data["email"]
    existing_user = user_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email already exists")
    hash_password = pwd_context.hash(data["password"])
    new_user = {
        "email": data["email"],
        "user_name": data["user_name"],
        "password": hash_password
    }
    result = user_collection.insert_one(new_user)
    if not result.acknowledged:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm dữ liệu vào cơ sở dữ liệu")
    user_data = {
        "email": data["email"],
        "user_name": data["user_name"]
    }
    return {"user": user_data}


@router.put("/update_user_info", tags = ["user"])
async def update_user_info(user_id: str, data: Annotated[dict, Body(...)]):
    result = user_collection.update_one(
        {"user_id": user_id},
        {"$set": {**data}}
    )
    if result.modified_count > 0: 
        return "Cập nhật thành công"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi cập nhật thông tin")