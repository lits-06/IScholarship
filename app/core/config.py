from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    SECRET_KEY: str = "2af5638279b026d8ee2f2e5089ac7b7e0f4250f98af9e78699d1ca0526e33a8c"
    ALGORITHM: str = "HS256"
    COOKIE_NAME: str = "access_token"

settings = Setting()