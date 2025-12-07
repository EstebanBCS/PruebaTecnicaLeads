from pydantic import BaseModel, EmailStr

class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    restaurant_type: str
    city: str

class LeadResponse(LeadCreate):
    id: int
    lat: float | None = None
    lon: float | None = None

    class Config:
        orm_mode = True

class SearchQuery(BaseModel):
    query: str