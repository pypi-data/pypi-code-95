from marshmallow import Schema, fields


class EventPipelineSchema(Schema):
    name = fields.String(required=True)
    version = fields.String(required=True)
    user = fields.String(required=True)


class EventMetadataSchema(Schema):
    task_name = fields.String(required=True)
    task_version = fields.String(required=True)
    task_environment = fields.String(required=True)


class EventDataSchema(Schema):
    payload = fields.Dict(required=True)
    type = fields.String(required=True)
    uri = fields.String(required=True)
    source = fields.String(required=True)
    destination = fields.String(required=True)


class EventReporterSchema(Schema):
    name = fields.String(required=True)


class ClientEventSchema(Schema):
    pipeline = fields.Nested(EventPipelineSchema(), required=True)
    event = fields.Nested(EventMetadataSchema(), required=True)
    data = fields.Nested(EventDataSchema(), required=True)
    reporter = fields.Nested(EventReporterSchema(), required=True)

class VeriteosClientSchema(Schema):
    sentinel_uri = fields.Url(required=True)
    should_send_data = fields.Boolean(required=True)
