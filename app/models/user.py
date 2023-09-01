from pydantic import BaseModel

class User(BaseModel):
    gmail: str
    password: str
    username: str