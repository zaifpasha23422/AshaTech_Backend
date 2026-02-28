from pydantic import BaseModel,Field,EmailStr , field_validator
from typing import Optional
from enum import Enum
from schema.enum import UserRole

class MessageCreate(BaseModel):
    name: str = Field(max_length=20,min_length=3)
    email: EmailStr = Field
    phone_no: str = Field(max_length=18,min_length=8)
    subject: str = Field
    message: Optional[str] = Field(max_length=200)

    
class UserCreate(BaseModel):
    name: str = Field(max_length=20,min_length=3)
    email:EmailStr = Field
    phone_no: str = Field(max_length=18,min_length=8)
    role:UserRole = UserRole.user
    @field_validator("role", mode="before")
    @classmethod 
    def empty_string_to_default(cls, v):
        if v == "":
            return UserRole.user
        return v
    password: str =Field(max_length=18, min_length=6)
    
class UserLogin(BaseModel):
    email: str = Field(..., description="email")
    password:str = Field(...,min_length=8, max_length=18)