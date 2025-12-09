from sqlalchemy.orm import Session
from app.db import Base, engine, SessionLocal
from app.schemas import Lead
from app.models import LeadCreate, LeadResponse, SearchQuery
from app.services.api_client import fetch_city_info
from app.services.vector_service import find_most_similar_by_name
from fastapi import FastAPI, Depends, HTTPException, status  
from typing import List
from fastapi import Query


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Raiz Unicamente para dar a conocer que se levanto correctamente
@app.get("/")  
def root():
    return {"message": "Servidor Funcionando Correctamente"}


#Crear Lead
@app.post("/api/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    # Verificar duplicado
    existing_email = db.query(Lead).filter(Lead.email == lead.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un lead con ese email"
        )

    # Intentar obtener datos externos
    try:
        external = await fetch_city_info(lead.city)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio externo de ubicación falló"
        )

    new_lead = Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        restaurant_type=lead.restaurant_type,
        city=lead.city,
        lat=external.get("lat"),
        lon=external.get("lon")
    )

    try:
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al guardar el lead en la base de datos"
        )

    return new_lead

#Listar todos los Leads
@app.get("/api/leads", response_model=list[LeadResponse])
def list_leads(db: Session = Depends(get_db)):
    try:
        return db.query(Lead).all()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudieron obtener los leads"
        )

#Buscar con query
@app.post("/api/leads/search")
def search_lead_similar(request: SearchQuery, db: Session = Depends(get_db)):
    results = find_most_similar_by_name(request.query, db, top_k=3)

    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron leads similares")

    # Convertir la salida
    response = []
    for lead, score in results:
        response.append({
            "match": LeadResponse.from_orm(lead),
            "score": round(score, 3)
        })

    return {"results": response}



#Obtener Health
@app.get("/api/health")
def health_check():
    return {"status": "ok"}



#Eliminar
@app.delete("/api/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead no encontrado"
        )

    db.delete(lead)
    db.commit()
