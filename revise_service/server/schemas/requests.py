from marshmallow import validate, Schema, fields
from marshmallow_enum import EnumField

from core.entities.Enums import Vat, PaymentType


class StartReviseSchema(Schema):
    revise_id = fields.String(validate=validate.Length(max=11), required=True)
    date_from = fields.Date(format="%Y-%m-%d", required=True)
    date_to = fields.Date(format="%Y-%m-%d", required=True)
    need_cash = fields.Bool(required=True)
    need_non_cash = fields.Bool(required=True)
    need_tickets = fields.Bool(required=True)
    need_documents = fields.Bool(required=True)
    region_id = fields.String(validate=validate.Length(max=5))
    company_inn = fields.String(validate=validate.Length(equal=10))
    company_kpp = fields.String(validate=validate.Length(equal=9))
    email = fields.Email()
