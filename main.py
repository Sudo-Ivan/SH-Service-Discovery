from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from db.database import init_db, reset_db
from services import router as services_router
from detect import router as detect_router 
from fastapi.middleware.cors import CORSMiddleware
import secrets
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

session_token = ""

def generate_session_token():
    return secrets.token_urlsafe(32)

def verify_reset_token(token: str):
    if token != session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )

app.include_router(services_router)
app.include_router(detect_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    global session_token
    session_token = generate_session_token()
    init_db()
    logging.info(f"Session token for DB reset: {session_token}")

@app.get("/reset-db")
async def reset_database(token: str = Depends(verify_reset_token)):
    reset_db()
    return {"detail": "Database reset successfully"}

cors_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)