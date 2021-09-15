from marshmallow import EXCLUDE, Schema, fields, post_load
from marshmallow_enum import EnumField

from snatch.base.data import BaseData
from snatch.base.status import IntegrationStatus


class BaseSchema(Schema):
    """Base DataSource Schema.

    Add a subclass for each Datasource and his specific fields.

    """

    tax_id = fields.Str(allow_none=True)
    prospect_date = fields.DateTime(allow_none=True, data_key="prospect_end_date")
    integration_status = EnumField(IntegrationStatus, data_key="status")
    status_reason = fields.Str(default="")

    @post_load
    def make_data(self, data, **kwargs):
        new_data = BaseData(**data)
        return new_data

    class Meta:
        unknown = EXCLUDE
