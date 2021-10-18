from enum import Enum

from marshmallow import Schema, fields, validate, post_dump
from marshmallow_enum import EnumField


class MegapolisApiErrorType(Enum):
    WRONG_TOKEN = 1
    WRONG_FIELDS_FORMAT = 2
    UNKNOWN_COMPANY = 3
    TICKET_DOESNT_EXISTS = 4
    TICKET_ALREADY_EXISTS = 5
    WRONG_LOGIN_OR_PASSWORD = 6


class ValidationErrorSchema(Schema):
    field_name = fields.String(validate=validate.Length(max=55))
    message = fields.String(validate=validate.Length(max=155))


class ErrorSchema(Schema):
    error_id = fields.Integer()
    type = EnumField(MegapolisApiErrorType)
    text = fields.String()
    fields = fields.List(fields.Nested(ValidationErrorSchema))

    @post_dump
    def clean_missing(self, data, **kwargs):
        tmp = list(filter(lambda key: data[key] is None, data))
        for key in tmp:
            data.pop(key)
        return data
