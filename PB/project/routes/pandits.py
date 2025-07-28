# from fastapi import APIRouter
# from db import db
# from fastapi import Query

# router = APIRouter()

# @router.get("/all")
# def get_all_pandits():
#     return list(db.pandits.find({}, {"_id": 0, "password": 0}))

# @router.post("/filter")
# def filter_pandits(language: list[str] = Query([]), location: str = "", experience: int = 0):
#     query = {}
#     if language:
#         query["language"] = {"$in": language}
#     if location:
#         query["location"] = location
#     if experience:
#         query["experience"] = {"$gte": experience}
#     return list(db.pandits.find(query, {"_id": 0, "password": 0}))


from fastapi import APIRouter
from db import db
from fastapi import Query
from bson import ObjectId

router = APIRouter()

def serialize(doc):
    return {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items()}

@router.get("/all")
def get_all_pandits():
    pandits = db.pandits.find({}, {"password": 0})
    return [serialize(p) for p in pandits]

@router.post("/filter")
def filter_pandits(language: list[str] = Query([]), location: str = "", experience: int = 0):
    query = {}
    if language:
        query["language"] = {"$in": language}
    if location:
        query["location"] = location
    if experience:
        query["experience"] = {"$gte": experience}
    filtered = db.pandits.find(query, {"password": 0})
    return [serialize(p) for p in filtered]
