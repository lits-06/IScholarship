from fastapi import FastAPI

from .router import achievement, scholarship, scholarship_user, user

app = FastAPI()

app.include_router(achievement.router, prefix="/api")
app.include_router(scholarship.router, prefix="/api")
app.include_router(scholarship_user.router, prefix="/api")
app.include_router(user.router, prefix="/api")

@app.get("/")
def read_root():
    return {"Hello": "World"}


