from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password: str

class Pandit(BaseModel):
    name: str
    email: EmailStr
    password: str
    language: List[str]
    location: str
    experience: int

class Booking(BaseModel):
    userId: str
    panditId: str
    date: str
    time: str
    purpose: Optional[str] = None

class PalmistryUpload(BaseModel):
    userId: str
    image_url: str