from pydantic import BaseModel

class Service(BaseModel):
    host: str
    port: int
    service: str
    status: str
    previewImage: str