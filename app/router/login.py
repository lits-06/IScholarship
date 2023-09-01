from fastapi import APIRouter

from ..db.mongo import connect_to_mongo
from ..models.user import User

router = APIRouter()

# API /api/login_with_google nhận vào JSON gồm gmail và username dạng 
# {"gmail": "shiraishi2612@gmail.com",
#  "username": "Đoàn Dũng"} 
# từ đó query vào mongo để trả về user nếu có rồi, hoặc tạo mời user nếu chưa có với pass 123 (sau này sẽ thay đổi)
@router.get("/login-google", tags = ["login"])
async def login_with_google(data: dict):
    # nhận gmail từ FE
    gmail = data["gmail"]

    # kết nối db
    db = connect_to_mongo()
    user_collection = db["user"]

    existing_user = user_collection.find_one({"gmail": gmail})

    if existing_user:
        return User(**existing_user)
    else:
        new_user = {
            "gmail": gmail,
            "username": data["username"],
            "password": 123
        }
        user_collection.insert_one(new_user)
        return new_user

    