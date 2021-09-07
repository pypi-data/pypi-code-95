from typing import TypedDict, Optional
from jsonclasses.jobject import JObject

class CorsSetting(TypedDict):
    allow_headers: Optional[str]
    allow_origin: Optional[str]
    allow_methods: Optional[str]


class OperatorSetting(TypedDict):
    operator_cls: type[JObject]
    encode_key: str
