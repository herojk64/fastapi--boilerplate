from pydantic import BaseModel, EmailStr
from typing import Optional

from src.models.schemas.user import UserOut


class SignupIn(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenWithUserOut(TokenOut):
    user: UserOut
