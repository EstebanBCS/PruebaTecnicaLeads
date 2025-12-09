import unicodedata
import re
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
from app.schemas import Lead

#Ejemplos de Abreviaciones
CITY_ABBREVIATIONS = {
    "mzt": "mazatlan",
    "tj": "tijuana",
    "cdmx": "ciudad de mexico",
    "gdl": "guadalajara",
    "mty": "monterrey",
    "qro": "queretaro",
}

def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()

#Funcion Basica para las abreviaciones
def expand_abbreviation(text: str) -> str:
    t = normalize(text)
    return CITY_ABBREVIATIONS.get(t, t)


def str_similarity(a: str, b: str) -> float:
    """Ratio de similitud entre dos strings (0-1)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def token_overlap_score(query_tokens: set, target_tokens: set) -> float:
    if not query_tokens or not target_tokens:
        return 0.0
    inter = query_tokens & target_tokens
    # Jaccard-like: |A∩B| / |A∪B|
    union = query_tokens | target_tokens
    return len(inter) / max(1, len(union))

#Funcion para encontrar el mas similar por el Nombre en este caso se apoya de las abreviaciones que agregamos al inicio
def find_most_similar_by_name(query: str, db: Session, top_k: int = 3):
    q = expand_abbreviation(query)
    if not q:
        return [], []

    leads = db.query(Lead).all()
    if not leads:
        return [], []

    scored = []

    for lead in leads:
        full = f"{lead.name} {lead.restaurant_type} {lead.city}"
        t = normalize(full)

        score = 0

        # 1) Coincidencia restaurante
        if normalize(lead.restaurant_type) in q:
            score += 2
        
        # 2) Coincidencia ciudad o abreviación
        city_norm = normalize(lead.city)
        if city_norm in q or q in city_norm:
            score += 1


        # 3) Similitud proporcional por letras en común
        name = normalize(lead.name)
        common = len(set(q) & set(name))
        score += common / max(len(q), len(name))

        # 4) Bonus iniciales (ej. mzt con mazatlan)
        if q[:2] == name[:2]:
            score += 0.5

        scored.append((lead, score))

    # Ordenar por score
    scored.sort(key=lambda x: x[1], reverse=True)

    # Tomar solo TOP-K
    return scored[:top_k]

