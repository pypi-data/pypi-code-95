# -*- coding: utf-8 -*-
from pymongo import (
    ASCENDING,
    DESCENDING,
)
from kiwoomde.database.mongo import generate_mongodb
db, bkdb = generate_mongodb()
from kiwoomde.database.schema import SchemaModel
from kiwoomde.database.collection import (
    DataModel,
    SelectorModel,
)
