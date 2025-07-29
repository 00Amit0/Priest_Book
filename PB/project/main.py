from fastapi import FastAPI
from routes import auth, pandits, bookings, ai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from your frontend origin (e.g., localhost:3000 for React)
# origins = [
#     "http://localhost:3000",   # React (default port)
#     "http://127.0.0.1:3000",   # Alternative local access
#     # Add more origins as needed
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allows listed frontend origins
    allow_credentials=True,
    allow_methods=["*"],              # Allows all HTTP methods
    allow_headers=["*"],              # Allows all headers
)

app.include_router(auth.router, prefix="/auth")
app.include_router(pandits.router, prefix="/pandits")
app.include_router(bookings.router, prefix="/bookings")
app.include_router(ai.router, prefix="/ai")

@app.get("/")
def root():
    return {"message": "Pandit Booking API Running"}
