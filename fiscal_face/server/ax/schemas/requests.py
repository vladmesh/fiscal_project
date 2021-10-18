from marshmallow import validate, Schema, fields


class CashboxRegisterSchema(Schema):
    cashbox_id = fields.Integer()
    register_type = fields.Integer(validate=validate.Range(min=0, max=2))
    reason = fields.Integer(allow_none=True)


class CloseFNSchema(Schema):
    cashbox_id = fields.Integer()
    inn = fields.String(validate=validate.Length(min=10, max=12))
    authorized_person_name = fields.String()


class GetCashboxData(Schema):
    cashbox_id = fields.Integer()
