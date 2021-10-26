from marshmallow import validate, Schema, fields


class StartReviseSchema(Schema):
    revise_id = fields.String(validate=validate.Length(max=11), required=True)
    date_from = fields.Date(format="%Y-%m-%d", required=True)
    date_to = fields.Date(format="%Y-%m-%d", required=True)
    need_cash = fields.Bool(required=True)
    need_non_cash = fields.Bool(required=True)
    need_tickets = fields.Bool(required=True)
    need_documents = fields.Bool(required=True)
    companies = fields.List(fields.String(), required=True)
    email = fields.Email()
