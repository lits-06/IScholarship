from fastapi import HTTPException, status, Request
from jose import jwt, JWTError


from app.core.model import OAuth2PasswordBearerWithCookie
from app.core.config import settings


oauth2_scheme1 = OAuth2PasswordBearerWithCookie(tokenUrl = "/api/login")
oauth2_scheme2 = OAuth2PasswordBearerWithCookie(tokenUrl = "/api/login-google")


def decode_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials."
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("user_id")
        if not user_id:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception
    
    return user_id


def get_current_user_from_cookie(request: Request):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail = "Không thể xác thực thông tin"
    )
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise credentials_exception
    user_id = decode_token(token)
    return user_id