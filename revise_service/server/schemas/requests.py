from core.entities.entity_schemas import TicketSchema, DocumentSchema
from marshmallow import Schema, fields, validate


class InsertTicketsAsuopSchema(Schema):
    tickets = fields.List(fields.Nested(TicketSchema))
    company_id = fields.String()


class InsertDocumentsAsuopSchema(Schema):
    documents = fields.List(fields.Nested(DocumentSchema))
    company_id = fields.String()


class BindDocumentsSchema(Schema):
    useDateTime = fields.Boolean()


class StartReviseSchema(Schema):
    date_from = fields.Date(format="%Y-%m-%d", required=True)
    date_to = fields.Date(format="%Y-%m-%d", required=True)
    need_cash = fields.Bool(required=True)
    need_non_cash = fields.Bool(required=True)
    need_tickets = fields.Bool(required=True)
    need_documents = fields.Bool(required=True)
    companies = fields.List(fields.String(), required=True, validate=validate.Length(min=1))
    email = fields.Email()
