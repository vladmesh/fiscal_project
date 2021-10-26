from marshmallow import Schema, fields
from core.entities.entity_schemas import TicketSchema, DocumentSchema


class InsertTicketsAsuopSchema(Schema):
    tickets = fields.List(fields.Nested(TicketSchema))
    company_id = fields.String()


class InsertDocumentsAsuopSchema(Schema):
    documents = fields.List(fields.Nested(DocumentSchema))
    company_id = fields.String()


class BindDocumentsSchema(Schema):
    useDateTime = fields.Boolean()
