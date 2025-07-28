# from fastapi import APIRouter, HTTPException
# from models import Booking
# from db import db

# router = APIRouter()

# @router.post("/book")
# def book_pandit(booking: Booking):
#     db.bookings.insert_one(booking.dict())
#     return {"message": "Pandit booked successfully"}

# @router.get("/{panditId}")
# def get_bookings(panditId: str):
#     return list(db.bookings.find({"panditId": panditId}, {"_id": 0}))


from fastapi import APIRouter, HTTPException
from models import Booking
from db import db
from bson import ObjectId

router = APIRouter()

def serialize(doc):
    return {k: str(v) if isinstance(v, ObjectId) else v for k, v in doc.items()}

@router.post("/book")
def book_pandit(booking: Booking):
    result = db.bookings.insert_one(booking.dict())
    return {"message": "Pandit booked successfully", "bookingId": str(result.inserted_id)}

@router.get("/{panditId}")
def get_bookings(panditId: str):
    bookings = db.bookings.find({"panditId": panditId})
    return [serialize(b) for b in bookings]
