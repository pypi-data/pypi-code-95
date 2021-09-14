"""Preflight requests related model classes."""

from pydantic import BaseModel
from pydantic.fields import Field


class Preflight(BaseModel):
    """Credit information for a given request. """

    detail: int = Field(..., example=3, description="Cost in credits of a given request.")

    class Config:
        schema_extra = {
            "example": {
                "detail": 3
            }
        }
