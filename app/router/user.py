from fastapi import APIRouter, HTTPException, status, Request
from bson import ObjectId

from db.mongo import db
from core.security import get_password_hash, create_access_token, authenticate_user, verify_password
from core.config import settings
from core.form import LoginForm, LoginGoogleForm
from router.deps import get_user_id
from core.model import Token

router = APIRouter()
user_collection = db["user"]


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
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email đã tồn tại")
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


@router.get("/get_user_info")
async def get_user_info(request: Request):
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    projection = {"_id": False, "password": False}
    result = user_collection.find_one({"_id": ObjectId(user_id)}, projection)
    if "education_level" not in result:
        user_collection.update_one({"email": result["email"]}, {"$set": {"education_level": None}})
    if "nationality" not in result:
        user_collection.update_one({"email": result["email"]}, {"$set": {"nationality": None}})
    if "sex" not in result:
        user_collection.update_one({"email": result["email"]}, {"$set": {"sex": None}})
    if "date_of_birth" not in result:
        user_collection.update_one({"email": result["email"]}, {"$set": {"date_of_birth": None}})
    if "phone" not in result:
        user_collection.update_one({"email": result["email"]}, {"$set": {"phone": None}})
    data = user_collection.find_one({"_id": ObjectId(user_id)}, projection)
    return data


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

    
