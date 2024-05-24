from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from config import get_cors_origins
from db.database import init_db
from services import router as services_router
from detect import router as detect_router 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(services_router)
app.include_router(detect_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    init_db()

cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)