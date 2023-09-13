from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Response, Depends, Request
from bson import ObjectId

from ..db.mongo import db
from app.core.security import get_password_hash, create_access_token, authenticate_user, verify_password
from app.core.config import settings
from app.core.form import LoginForm, LoginGoogleForm
from app.router.deps import get_user_id
from app.core.model import Token

router = APIRouter()
user_collection = db["user"]


# @router.post("/token", response_model = Token)
# def get_access_token(user_id: str):
#     access_token = create_access_token(data={"user_id": user_id})
#     return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


@router.post("/login")
async def login(data: dict):
    user = user_collection.find_one({"email": data["email"]})
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy email")
    hash_password = user["password"]
    if not verify_password(data["password"], hash_password):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Sai mật khẩu")
    access_token = create_access_token(data={"user_id": str(user["_id"])})
    return {settings.COOKIE_NAME: access_token, "user_id": str(user["_id"])}


@router.post("/login-google")
async def login_with_google(data: dict):
    email = data["email"]
    user = user_collection.find_one({"email": email})
    if user:
        access_token = create_access_token(data={"user_id": str(user["_id"])})
        return {settings.COOKIE_NAME: access_token, "user_id": str(user["_id"])}
    else:
        new_user = {
            "email": email,
            "user_name": data["user_name"]
        }
        result = user_collection.insert_one(new_user)
        if not result.acknowledged:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm dữ liệu vào cơ sở dữ liệu")
        access_token = create_access_token(data={"user_id": str(result.inserted_id)})
        return {settings.COOKIE_NAME: access_token, "user_id": str(result.inserted_id)}


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
async def update_user_info(request: Request, data: dict):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {**data}}
    )
    if result.modified_count > 0: 
        return "Cập nhật thành công"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi cập nhật thông tin")
    
    
