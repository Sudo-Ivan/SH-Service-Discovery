from fastapi import APIRouter
from db.database import get_services_from_db, add_service_to_db
from models import Service

router = APIRouter()

@router.get("/services")
def fetch_services():
    services_raw = get_services_from_db()
    # Convert raw services into Pydantic models or similar structure for response
    return {"services": services_raw}