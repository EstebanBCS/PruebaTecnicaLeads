import os
import httpx
from dotenv import load_dotenv

load_dotenv()

EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL")
USER_AGENT = os.getenv("USER_AGENT", "FastAPI-Lead-App")

async def fetch_city_info(city: str):
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(EXTERNAL_API_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception:
            return {"lat": None, "lon": None}

    if not data:
        return {"lat": None, "lon": None}

    return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
