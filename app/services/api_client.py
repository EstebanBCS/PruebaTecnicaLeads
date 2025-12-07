import httpx

BASE_URL = "https://nominatim.openstreetmap.org/search"

async def fetch_city_info(city: str):
    """
    Obtiene latitud y longitud de una ciudad usando OpenStreetMap Nominatim.
    """
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    
    headers = {
        "User-Agent": "FastAPI-Lead-App"  # recomendado por Nominatim
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception:
            return {"lat": None, "longitude": None}

    if not data:
        return {"lat": None, "longitude": None}

    return {
        "lat": float(data[0]["lat"]),
        "longitude": float(data[0]["lon"])
    }
