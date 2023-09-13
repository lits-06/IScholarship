from fastapi import HTTPException, status
from jose import jwt, JWTError
from pydantic import ValidationError


from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/api/token")


def get_user_id(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials."
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = settings.ALGORITHM)
    except JWTError:
        raise credentials_exception
    except ValidationError:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Lỗi khi kiểm tra dữ liệu")
    user_id: str = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Không tìm thấy user")
    return user_id








