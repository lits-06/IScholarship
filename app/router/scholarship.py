from fastapi import APIRouter, HTTPException, status
from math import ceil

from ..db.mongo import db

router = APIRouter()
scholarship_collection = db["scholarship"]


@router.post("/create_scholarship", tags = ["scholarship"])
async def create_scholarship(data: dict):
    result = scholarship_collection.insert_one(data)
    if result.inserted_id:
        return "Thêm học bổng thành công"
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm học bổng")


@router.post("/create_scholarship_list", tags = ["scholarship"])
async def create_scholarship_list(data: list[dict]):
    for scholarship in data:
        result = scholarship_collection.insert_one(scholarship)
        if not result.inserted_id:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi thêm học bổngt")
    return "Thêm bài viết thành công"


# nhập vào trang hiện tại là trang bao nhiêu int
@router.get("/get_scholarship/{page}", tags = ["scholarship"])
async def get_scholarship(page: int):
    total_scholarship = scholarship_collection.count_documents({})
    total_page = ceil(total_scholarship / 10)
    skip_count = (page - 1) * 10
    cursor = scholarship_collection.find().skip(skip_count).limit(10)
    scholarship = list(cursor)
    if scholarship:
        return {"total_page": total_page, "scholarship": scholarship}
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Lỗi khi tìm học bổng")
    

@router.get("/get_all_type", tags = ["scholarship"])
async def get_all_type():
    type = scholarship_collection.distinct("type")
    if type:
        return {"data": type}
    else:
        return {"data": []}
    

@router.get("/get_all_educationlevel", tags = ["scholarship"])
async def get_all_educationlevel():
    level = scholarship_collection.distinct("educational_level")
    if level:
        return {"data": level}
    else:
        return {"data": []}