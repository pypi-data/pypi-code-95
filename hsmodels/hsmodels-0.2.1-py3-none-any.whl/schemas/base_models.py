from datetime import datetime
from typing import Any, Dict, Type

from pydantic import BaseModel


class BaseMetadata(BaseModel):
    class Config:
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model) -> None:
            if hasattr(model.Config, "schema_config"):
                schema_config = model.Config.schema_config
                if "read_only" in schema_config:
                    # set readOnly in json schema
                    for field in schema_config["read_only"]:
                        schema['properties'][field]['readOnly'] = True


class BaseCoverage(BaseMetadata):
    def __str__(self):
        return "; ".join(
            [
                "=".join([key, val.isoformat() if isinstance(val, datetime) else str(val)])
                for key, val in self.__dict__.items()
                if key != "type" and val
            ]
        )
