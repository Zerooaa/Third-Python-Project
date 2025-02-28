from pydantic import BaseModel, Field
from typing import Optional

class Admin(BaseModel):
    admin_id: int 
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=50)
    role: str = Field(...,)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
