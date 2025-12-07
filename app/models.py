from pydantic import BaseModel, EmailStr

class CrearLead(BaseModel):
    name: str
    email: EmailStr
    phone: str
    restaurant_type: str
    city: str
    lat: float | None = None
    longitude: float | None = None
    
class RespuestaLead(CrearLead):
    id: int
    name: str
    lat: float | None = None
    longitude: float | None = None