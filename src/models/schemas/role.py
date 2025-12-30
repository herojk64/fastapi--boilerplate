from typing import Optional
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    id: int

    class Config:
        from_attributes = True
