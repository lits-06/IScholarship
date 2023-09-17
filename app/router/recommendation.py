from fastapi import APIRouter, HTTPException, status, Request
from math import ceil
from bson import ObjectId
import re

from db.mongo import db
from router.deps import get_user_id
# from ..middlewares.recommend import turn_json_to_df, cast_to_atomic_file, load_dataset, train_model, get_top_k_item, get_top_k_item_context
from middlewares.bm25 import create_string_list, get_top_k_item_bm25
# from recbole.quick_start import load_data_and_model
import os


router = APIRouter()
user_collection = db["user"]
scholarship_collection = db["scholarship"]
scholarshipuser_collection = db["scholarshipuser"]
achievement_collection = db["achievement"]


@router.get("/get_all_model")
async def get_all_model():
    cursor_user = user_collection.find()
    user = [user_doc | {"_id": str(user_doc["_id"])} for user_doc in cursor_user]

    cursor_scholarship = scholarship_collection.find()
    scholarship = [scholarship_doc | {"_id": str(scholarship_doc["_id"])} for scholarship_doc in cursor_scholarship]

    cursor_scholarshipuser = scholarshipuser_collection.find()
    scholarshipuser = [scholarshipuser_doc | {"_id": str(scholarshipuser_doc["_id"])} for scholarshipuser_doc in cursor_scholarshipuser]
    
    return {"user": user, "scholarship": scholarship, "scholarshipuser": scholarshipuser}


@router.post("/get_recommendation")
async def get_recommendation(data: dict):
    query = {}
    if "type" in data:
        query["type"] = data["type"]
    if "education_level" in data:
        regex_pattern = re.compile(fr".*{data['education_level']}.*")
        query["education_level"] = {"$regex": regex_pattern}
    if "major" in data:
        regex_pattern = re.compile(fr".*{data['major']}.*")
        query["major"] = {"$regex": regex_pattern}
    cursor = scholarship_collection.find(query).skip(0).limit(10)
    result = [record | {"_id": str(record["_id"])} for record in cursor]
    return result
    

@router.get("/train_model")
async def get_all_data():
    # if method == "BM25":
    cursor_scholarship = scholarship_collection.find()
    scholarship = [scholarship_doc | {"_id": str(scholarship_doc["_id"])} for scholarship_doc in cursor_scholarship]
    create_string_list(scholarship)
    return {"status": 200}
    # else:
    #     cursor_user = user_collection.find()
    #     user = [user_doc | {"_id": str(user_doc["_id"])} for user_doc in cursor_user]

    #     cursor_scholarship = scholarship_collection.find()
    #     scholarship = [scholarship_doc | {"_id": str(scholarship_doc["_id"])} for scholarship_doc in cursor_scholarship]

    #     cursor_scholarshipuser = scholarshipuser_collection.find()
    #     scholarshipuser = [scholarshipuser_doc | {"_id": str(scholarshipuser_doc["_id"])} for scholarshipuser_doc in cursor_scholarshipuser]
        
    #     train_model(scholarshipuser, user, scholarship, "general", "BPR")
    #     return {"status": 200}


@router.get("/recommend")
async def recommendation(request: Request, type_model: str, model:str, method: str, k: int):
    #if method == 'BM25':
    token = request.headers.get('authorization')
    user_id = get_user_id(token)
    achievements = achievement_collection.find({"user_id": user_id})
    achievements_list = []
    for achievement in achievements:
        achievement.pop("_id", None)  # Loại bỏ ObjectId
        achievements_list.append(achievement)
    directory = os.path.dirname('app/middlewares/bm25/')
    file_path = os.path.join(directory, 'scholarship.txt')
    list_recommend = get_top_k_item_bm25(achievements_list, file_path, k)
    return {"recommend": list_recommend}
    # else:
    #     config, model_train, data_set, train_data, valid_data, test_data = load_data_and_model(
    #         model_file=f'saved/{model}.pth',
    #     )
    #     if type_model == "general":
    #         topk_score, topk_iid_list = get_top_k_item([user_id], data_set, model_train, test_data, config, 1)
    #     else:
    #         topk_score, topk_iid_list = get_top_k_item_context([user_id], data_set, model_train, test_data, config, 1)
    #     return topk_score, topk_iid_list 
