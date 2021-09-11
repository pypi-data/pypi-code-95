from typing import Any,List,Optional
import joblib
from fastapi import APIRouter, HTTPException
from loguru import logger


from model.prediction import HealthResponse, MachineLearningReponse
from core.errors import PredictException
from services.predict import MachineLearningModel

router = APIRouter()
model = MachineLearningModel()

get_prediction = lambda data_input: MachineLearningReponse(
    model.predict(data_input)
)

@router.post("/predict", response_model=MachineLearningReponse, name="predict:get-prediction")
async def predict(data_input : List[float] = None) -> MachineLearningReponse:
    if not data_input:
        raise HTTPException(status_code=404, detail=f"'data_input' argument invalid!")
    try:
        # prediction = get_prediction(data_input)
        prediction = model.predict(data_input)
    except Exception as e:
        raise ValueError("Hello")
        raise HTTPException(status_code=500, detail=f"Exception: {e}")

    return MachineLearningReponse(prediction = prediction)


@router.get("/health", response_model= HealthResponse, name = "health:get-data")
async def health_check():
    is_health = False
    try:
        input_sample = [6.2,2.8,4.8,1.8]
        # get_prediction(input_sample)
        prediction = model.predict(data_input)
        is_health = True
        return HealthResponse(status = is_health)
    except Exception:
        raise HTTPException(status_code=404, detail="Unhealthy")
