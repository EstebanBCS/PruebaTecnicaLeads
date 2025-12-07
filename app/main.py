from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import Base, engine, SessionLocal
from app.schemas import Lead
from app.models import LeadCreate, LeadResponse, SearchQuery
from app.services.api_client import fetch_city_info
from app.services.vector_service import find_most_similar_by_name  

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")  # Ruta raíz
def root():
    return {"message": "Servidor Funcionando Correctamente"}

@app.post("/leads", response_model=LeadResponse)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    external = await fetch_city_info(lead.city)

    new_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        restaurant_type=lead.restaurant_type,
        city=lead.city,
        lat=external.get("lat"),
        lon=external.get("lon")
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return new_lead

@app.get("/leads", response_model=list[LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()

@app.post("/leads/search")
def search_lead_similar(request: SearchQuery, db: Session = Depends(get_db)):
    query = request.query 
    
    match, score = find_most_similar_by_name(query, db) 

    if not match:
        return {"match": None, "score": 0.0}

    return {
        "match": {
            "id": match.id,
            "name": match.name,
            "email": match.email,
            "phone": match.phone,
            "restaurant_type": match.restaurant_type,
            "city": match.city,
            "lat": match.lat,
            "lon": match.lon
        },
        "score": score
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}