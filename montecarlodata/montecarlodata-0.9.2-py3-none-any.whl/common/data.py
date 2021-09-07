from dataclasses import dataclass, field
from typing import Optional, Dict, List, Union

from box import Box
from dataclasses_json import dataclass_json, LetterCase, Undefined, CatchAll


@dataclass
class MonolithResponse:
    data: Optional[Union[Box, Dict]] = None
    errors: Optional[List[Dict]] = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class OnboardingConfiguration:
    connection_options: CatchAll  # ConnectionOptions

    connection_type: str

    validation_query: Optional[str] = None
    validation_response: Optional[str] = None

    connection_query: Optional[str] = None
    connection_response: Optional[str] = None

    warehouse_type: Optional[str] = None
    warehouse_name: Optional[str] = None

    job_limits: Optional[Dict] = None
    job_types: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.INCLUDE)
@dataclass
class ConnectionOptions:
    monolith_base_payload: CatchAll  # Base options passed to the monolith (e.g. host, db, etc.)

    # Client connection options
    dc_id: Optional[str] = None
    validate_only: Optional[bool] = False
    skip_validation: Optional[bool] = False
    skip_permission_tests: Optional[bool] = False
    auto_yes: Optional[bool] = False

    monolith_connection_payload: dict = field(init=False)  # Additional options passed to the monolith (from client)

    def __post_init__(self):
        self.monolith_connection_payload = {}

        if self.dc_id:
            self.dc_id = str(self.dc_id)
            self.monolith_connection_payload['dcId'] = self.dc_id
        if self.skip_validation:
            self.monolith_connection_payload['skipValidation'] = self.skip_validation
        if self.skip_permission_tests:
            self.monolith_connection_payload['skipPermissionTests'] = self.skip_permission_tests


@dataclass
class ValidationResult:
    has_warnings: bool
    credentials_key: str
