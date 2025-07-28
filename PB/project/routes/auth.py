# from fastapi import APIRouter, HTTPException
# from models import User, Pandit
# from db import db

# router = APIRouter()

# @router.post("/user/register")
# def register_user(user: User):
#     if db.users.find_one({"email": user.email}):
#         raise HTTPException(status_code=400, detail="User already exists")
#     db.users.insert_one(user.dict())
#     return {"message": "User registered"}

# @router.post("/pandit/register")
# def register_pandit(pandit: Pandit):
#     if db.pandits.find_one({"email": pandit.email}):
#         raise HTTPException(status_code=400, detail="Pandit already exists")
#     db.pandits.insert_one(pandit.dict())
#     return {"message": "Pandit registered"}


from fastapi import APIRouter, HTTPException
from models import User, Pandit
from db import db
from bson import ObjectId

router = APIRouter()

def serialize(doc):
    return {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items()}

@router.post("/user/register")
def register_user(user: User):
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")
    result = db.users.insert_one(user.dict())
    return {"message": "User registered", "userId": str(result.inserted_id)}

@router.post("/pandit/register")
def register_pandit(pandit: Pandit):
    if db.pandits.find_one({"email": pandit.email}):
        raise HTTPException(status_code=400, detail="Pandit already exists")
    result = db.pandits.insert_one(pandit.dict())
    return {"message": "Pandit registered", "panditId": str(result.inserted_id)}
