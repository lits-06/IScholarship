from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Response, Depends, Request
from bson import ObjectId

from ..db.mongo import db
from app.core.security import get_password_hash, create_access_token, authenticate_user
from app.core.config import settings
from app.core.form import LoginForm, LoginGoogleForm
from app.router.deps import get_user_id
from app.core.model import Token

router = APIRouter()
user_collection = db["user"]


@router.post("/token", response_model = Token)
def get_access_token(user_id: str):
    access_token = create_access_token(data={"user_id": user_id})
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


@router.post("/login")
async def login_for_access_token(data: dict):
    user = authenticate_user(data["email"], data["password"])
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Sai email hoặc mật khẩu")
    result = get_access_token(str(user["_id"]))
    return result



@router.post("/login-google")
async def login_with_google(data: dict):
    email = data["email"]
    existing_user = user_collection.find_one({"email": email})
    if existing_user:
        get_access_token(str(existing_user["_id"]))
        return "Đăng nhập thành công"
    else:
        new_user = {
            "email": email,
            "user_name": data["user_name"]
        }
        result = user_collection.insert_one(new_user)
        if not result.acknowledged:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm dữ liệu vào cơ sở dữ liệu")
        get_access_token(str(result.inserted_id))
        return "Đăng nhập thành công"


# @router.post("/login")
# async def login(data: dict):
#     email = data["email"]
#     existing_user = user_collection.find_one({"email": email})
#     if not existing_user:
#         raise HTTPException(status_code = 404, detail = "Không tìm thấy thông tin người dùng")
#     password = existing_user["password"]
#     if not verify_password(data["password"], password):
#         raise HTTPException(status_code = 401, detail = "Không xác thực")
#     print(existing_user)
#     user_data = {
#         "_id": str(existing_user["_id"]),
#         "email": existing_user["email"],
#         "user_name": existing_user["user_name"]
#     }
#     return {"user": user_data}


@router.post("/register")
async def register(data: dict):
    email = data["email"]
    existing_user = user_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email already exists")
    hash_password = get_password_hash(data["password"])
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


@router.put("/update_user_info")
async def update_user_info(data: dict, user_id: str = Depends(get_user_id)):
    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {**data}}
    )
    if result.modified_count > 0: 
        return "Cập nhật thành công"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi cập nhật thông tin")
    
    
