
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.predictor import predict_yield

app = FastAPI(
    title="NEXORA - Quantum Crop Yield Prediction API",
    description="Hybrid quantum-classical crop yield prediction prototype.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CropInput(BaseModel):
    rainfall_mm: float = Field(ge=0, le=1000)
    temperature_c: float = Field(ge=-10, le=60)
    soil_moisture_pct: float = Field(ge=0, le=100)
    ndvi: float = Field(ge=-1, le=1)


@app.get("/")
def home():
    return {
        "project": "NEXORA",
        "message": "Quantum Crop Yield Prediction API is running!",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "backend": "FastAPI",
        "project": "NEXORA",
    }


@app.post("/api/predict")
def predict(crop: CropInput):
    try:
        prediction = predict_yield(
            rainfall_mm=crop.rainfall_mm,
            temperature_c=crop.temperature_c,
            soil_moisture_pct=crop.soil_moisture_pct,
            ndvi=crop.ndvi,
        )

        return {
            "project": "NEXORA",
            "model": "Quantum Neural Network",
            "predicted_yield_tons_per_hectare": round(prediction, 3),
            "unit": "tons/hectare",
            "notice": (
                "Prototype estimate based on synthetic training data; "
                "not a validated agricultural forecast."
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        ) from exc