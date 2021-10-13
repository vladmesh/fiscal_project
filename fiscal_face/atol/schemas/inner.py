from enum import Enum

from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField


class MegapolisApiErrorType(Enum):
    WRONG_TOKEN = 1
    WRONG_FIELDS_FORMAT = 2
    UNKNOWN_COMPANY = 3
    WRONG_TAX = 4
    TICKET_DOESNT_EXISTS = 5


class ValidationErrorSchema(Schema):
    field_name = fields.String(validate=validate.Length(max=25))
    message = fields.String()


class ErrorSchema(Schema):
    error_id = fields.Integer()
    type = EnumField(MegapolisApiErrorType)
    text = fields.String()
    fields = fields.List(fields.Nested(ValidationErrorSchema), allow_none=True)
