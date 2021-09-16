import json
from enum import Enum


class DocItemBase(str, Enum):

    def __repr__(self):
        return json.dumps(self)


class AccessRights(DocItemBase):
    RESTRICTED = "restricted"
    INTERNAL = "internal"
    OPEN = "open"


class Pii(DocItemBase):
    TRUE = "true"
    FALSE = "false"


class Type(DocItemBase):
    EGG = "egg"
    DATAPRODUCT = "dataproduct"
    DATAPACKAGE = "datapackage"
    API = "api"
    TERM = "begrep"
    APPROVED_TERM = "godkjent_begrep"
    TABLE = "tabell"
    TABLEAU = "tableau"
    KAFKA_TOPIC = "kafka_topic"
    PURPOSE = "purpose"
    PERSON = "person"
    TEAM = "team"
    NAIS_TEAM = "nais_team"
    PARQUET = "parquet"
    BIGQUERY = "bigquery"
