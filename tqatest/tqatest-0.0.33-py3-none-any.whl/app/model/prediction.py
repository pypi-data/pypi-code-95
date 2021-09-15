from pydantic import BaseModel
from typing import Optional, List

class MachineLearningReponse(BaseModel):
    prediction: List[float]

class HealthResponse(BaseModel):
    status : bool