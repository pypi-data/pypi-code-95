from fastapi import APIRouter
from fastapi.routing import APIRoute

from api.routes import predictor

router = APIRouter()
router.include_router(predictor.router, tags = ["predictor"], prefix = "/v1")