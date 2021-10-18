from marshmallow import validate, Schema, fields
from marshmallow_enum import EnumField

from core.entities.Enums import Vat, PaymentType
from core.entities.entity_schemas import TicketSchema


class InsertTicketsAsuopSchema(Schema):
    tickets = fields.List(fields.Nested(TicketSchema))

class InsertDocumentsAsuopSchema(Schema):
    documents = fields.List(fields.Nested())

class GetTokenSchema(Schema):
    login = fields.String(validate=validate.Length(max=25))
    password = fields.String(validate=validate.Length(max=30))


class PostTicketSchema(Schema):
    ticket_id = fields.String(validate=validate.Length(max=30), required=True)
    vat = EnumField(Vat, required=True)
    price = fields.Integer(required=True)
    payment_type = EnumField(PaymentType, required=True)
    payment_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", required=True)
    company_inn = fields.String(validate=validate.Length(equal=10), required=True)
    company_kpp = fields.String(validate=validate.Length(equal=9), required=True)
    client_email = fields.Email(required=True)


class GetTicketSchema(Schema):
    ticket_id = fields.String(validate=validate.Length(max=50))
    company_inn = fields.String(validate=validate.Length(equal=10), required=True)
    company_kpp = fields.String(validate=validate.Length(equal=9), required=True)