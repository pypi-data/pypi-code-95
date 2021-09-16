from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MonitoringModel(BaseModel):
    status: str


@router.get("/_/status", status_code=200, response_model=MonitoringModel)
async def get_apiaries():
    """
    Moniroting route to know if the application is healthy
    """
    return {"status": "OK"}
