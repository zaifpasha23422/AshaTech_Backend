from pydantic import BaseModel, EmailStr
from typing import Optional, List

class section(BaseModel):
    heading: str
    content: str
    content2: Optional[str] = None
    content3: Optional[str] = None
    content4: Optional[str] = None
    content5: Optional[str] = None
    content6: Optional[str] = None          


class information(BaseModel):
    phone_no : List[str]
    email : EmailStr
    
class BlogCreate(BaseModel):
    img:str
    title: str
    introduction: str
    section: List[section]
    conclusion: str
    contact_information: information
    