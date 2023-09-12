from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Response, Depends, Request
from bson import ObjectId

from ..db.mongo import db
from app.core.security import get_password_hash, create_access_token, authenticate_user
from app.core.config import settings
from app.core.form import LoginForm, LoginGoogleForm
from app.router.deps import get_current_user_from_cookie

router = APIRouter()
user_collection = db["user"]


@router.post("/login")
async def login_for_access_token(response: Response, form_data: LoginForm = Depends()):
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Sai email hoặc mật khẩu")
    access_token = create_access_token(data = {"user_id": str(user["_id"])})
    response.set_cookie(
        key = settings.COOKIE_NAME, 
        value = f"Bearer {access_token}", 
        httponly = True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}



@router.post("/login-google")
async def login_with_google(response: Response, form_data: LoginGoogleForm = Depends()):
    email = form_data.email
    existing_user = user_collection.find_one({"email": email})
    if existing_user:
        access_token = create_access_token(data = {"user_id": str(existing_user["_id"])})
        response.set_cookie(
            key = settings.COOKIE_NAME, 
            value = f"Bearer {access_token}", 
            httponly = True
        )
        return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}
    else:
        new_user = {
            "email": email,
            "user_name": form_data.user_name
        }
        result = user_collection.insert_one(new_user)
        if not result.acknowledged:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm dữ liệu vào cơ sở dữ liệu")
        access_token = create_access_token(data = {"user_id": result.inserted_id})
        response.set_cookie(
            key = settings.COOKIE_NAME, 
            value = f"Bearer {access_token}", 
            httponly = True
        )
        return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


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
async def update_user_info(data: dict, request: Request, user_id: str = Depends(get_current_user_from_cookie)):
    result = user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {**data}}
    )
    if result.modified_count > 0: 
        return "Cập nhật thành công"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi cập nhật thông tin")