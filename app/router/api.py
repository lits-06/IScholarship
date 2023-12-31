from fastapi import APIRouter

from router import user, scholarship, scholarship_user, achievement, recommendation,task5

api_router = APIRouter()

api_router.include_router(user.router, prefix = "/api", tags = ["user"]) 
api_router.include_router(scholarship.router, prefix = "/api", tags = ["scholarship"]) 
api_router.include_router(scholarship_user.router, prefix = "/api", tags = ["scholarship_user"]) 
api_router.include_router(achievement.router, prefix = "/api", tags = ["achievement"]) 
api_router.include_router(recommendation.router, prefix = "/api", tags = ["recommend"]) 
api_router.include_router(task5.router,prefix="/api",tags = ["task5"])
