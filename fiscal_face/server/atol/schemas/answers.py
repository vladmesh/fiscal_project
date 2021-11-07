from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from enum import Enum

from core.entities.Enums import DocumentType
from server.atol.schemas.inner import ErrorSchema


class MegapolisAnswerStatus(Enum):
    OK = 0
    ERROR = 1
    IN_PROCESS = 2


class MegapolisApiAnswerSchema(Schema):
    error = fields.Nested(ErrorSchema, allow_none=True)
    status = EnumField(MegapolisAnswerStatus)
    timestamp = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    answer = None


class GetTokenAnswerSchema(Schema):
    token = fields.String(validate=validate.Length(max=45))


class MegapolisApiAnswerSchemaGetToken(MegapolisApiAnswerSchema):
    answer = fields.Nested(GetTokenAnswerSchema, allow_none=True)


class PostTicketAnswerSchema(Schema):
    ticket_id = fields.String(validate=validate.Length(max=30))


class MegapolisApiAnswerSchemaPostTicket(MegapolisApiAnswerSchema):
    answer = fields.Nested(PostTicketAnswerSchema, allow_none=True)


class GetTicketAnswerSchema(Schema):
    fiscal_number = fields.Integer(validate=validate.Range(min=1, max=250000))
    fiscal_sign = fields.Integer()
    fiscal_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    fiscal_storage_number = fields.Integer()
    document_type = EnumField(DocumentType)


class MegapolisApiAnswerSchemaGetTicket(MegapolisApiAnswerSchema):
    answer = fields.Nested(GetTicketAnswerSchema)


