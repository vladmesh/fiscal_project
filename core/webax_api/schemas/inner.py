from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField

from core.entities.entities import SourceSettings
from revise_service.entities import SourceType


class SourceSettingsSchema(Schema):
    id = fields.String()
    type = EnumField(SourceType)
    address = fields.String()
    port = fields.Integer(strict=False, validate=validate.Range(min=0, max=65535))
    database_name = fields.String()
    login = fields.String()
    password = fields.String()
    query_new_tickets = fields.String()
    query_revise = fields.String()
    query_by_id = fields.String()

    @post_load
    def make_model(self, data, **kwargs):
        return SourceSettings(**data)
