# app/api/routes/ors.py

from fastapi import APIRouter
import requests
import os
from app.core.config import get_settings

router = APIRouter(prefix="/ors", tags=["ors"])


settings = get_settings()
ORS_KEY = settings.ors_api_key
print(f"ORS_KEY: {ORS_KEY}")  # Debugging line to check if the key is loaded correctly

@router.post("/directions")
async def directions(payload: dict):
    response = requests.post(
        "https://api.openrouteservice.org/v2/directions/driving-car/geojson",
        json=payload,
        headers={
            "Authorization": ORS_KEY,
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    return response.json()


@router.get("/reverse")
async def reverse(lat: float, lng: float):
    response = requests.get(
        f"https://api.openrouteservice.org/geocode/reverse",
        params={
            "api_key": ORS_KEY,
            "point.lon": lng,
            "point.lat": lat,
            "size": 1,
        },
        timeout=30,
    )

    return response.json()