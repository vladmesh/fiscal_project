from marshmallow import Schema, fields, validate, post_load

from core.entities import Company


class CompanySchema(Schema):
    id = fields.String()
    inn = fields.String(validate=validate.Length(10))
    kpp = fields.String(validate=validate.Length(9))
    name = fields.String(validate=validate.Length(max=50))
    full_name = fields.String()
    region = fields.String(validate=validate.Length(max=4))
    payment_place = fields.String(validate=validate.Length(max=25))
    authorized_person_name = fields.String(validate=validate.Length(max=80))
    agent_agent = fields.Integer(validate=validate.Range(min=0, max=1))
    tax = fields.Integer(validate=validate.Range(min=0, max=2))
    provider_name = fields.String()
    provider_phone = fields.String()
    additional_field_meaning = fields.String()
    additional_field_value = fields.String()

    @post_load
    def make_company(self, data, **kwargs):
        return Company(**data)

