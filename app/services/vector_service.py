from sqlalchemy.orm import Session
from app.schemas import Lead
import re
import math

#   Generar vector (más real)
def embed(text: str) -> list[float]:
    """
    Convierte texto a vector simple basado en:
    - Longitud
    - Número de palabras
    """
    length = len(text)
    words = len(text.split())
    return [float(length), float(words)]


#  Similitud entre vectores
def similarity(a: list[float], b: list[float]) -> float:
    """
    Similitud simple: comparación basada en longitud y número de palabras.
    """
    if a[0] == 0 or b[0] == 0:
        return 0.0
    
    # Normalizar diferencia
    diff = abs(a[0] - b[0]) + abs(a[1] - b[1]) 
    max_len = max(a[0], b[0]) + max(a[1], b[1])

    return 1 - (diff / max_len)


def clean(text: str) -> str:
    return re.sub(r"[^a-zA-ZáéíóúñüÁÉÍÓÚÑÜ\s]", "", text.lower())

def find_most_similar_by_name(query: str, db: Session):
    """
    Similitud por:
    + Coincidencia en tipo de restaurante (palabras clave)
    + Coincidencia de ciudad
    + Similaridad de longitud del nombre (desempate)
    """

    query_clean = clean(query)

    best_match = None
    best_score = -1

    leads = db.query(Lead).all()

    for lead in leads:
        txt = clean(f"{lead.name} {lead.restaurant_type} {lead.city}")
        
        score = 0
        
        # 1) Coincidencia por tipo (palabra dentro)
        if lead.restaurant_type.lower() in query_clean:
            score += 2  # Mayor peso

        # 2) Coincidencia ciudad
        if lead.city.lower() in query_clean:
            score += 1  

        # 3) Desempate por longitud
        score += 1 - abs(len(query_clean) - len(txt)) / max(len(query_clean), len(txt))

        if score > best_score:
            best_score = score
            best_match = lead

    return best_match, best_score
