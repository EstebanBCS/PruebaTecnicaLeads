from sqlalchemy.orm import Session
from app.models.lead import Lead

#   Embeddings simples
def embed(text: str) -> list[float]:
    """Representa un texto como un vector simple (longitud)."""
    return [float(len(text))]

def similarity(a: list[float], b: list[float]) -> float:
    """Similitud por longitud."""
    if a[0] == 0 or b[0] == 0:
        return 0.0
    return 1 - abs(a[0] - b[0]) / max(a[0], b[0])

#   Servicio de similitud
def find_most_similar_by_name(name: str, db: Session):
    """Busca el Lead con nombre más similar por vector de longitud."""
    embedded = embed(name)
    
    leads = db.query(Lead).all()
    if not leads:
        return None, 0.0

    best_match = None
    best_score = 0.0

    for lead in leads:
        vector_lead = embed(lead.name)
        score = similarity(embedded, vector_lead)

        if score > best_score:
            best_score = score
            best_match = lead

    return best_match, best_score
