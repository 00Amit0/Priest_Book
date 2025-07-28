from fastapi import FastAPI
from routes import auth, pandits, bookings, ai

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(pandits.router, prefix="/pandits")
app.include_router(bookings.router, prefix="/bookings")
app.include_router(ai.router, prefix="/ai")

@app.get("/")
def root():
    return {"message": "Pandit Booking API Running"}