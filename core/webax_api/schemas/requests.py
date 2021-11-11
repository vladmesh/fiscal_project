from marshmallow import Schema, fields

from core.entities.entity_schemas import TicketSchema, DocumentSchema


class WebaxRequest:
    def __init__(self, uid):
        self.action = uid


class UpdateStatusRequest(WebaxRequest):
    def __init__(self, rec_id, status, uid):
        self.status = status
        self.rec_id = rec_id
        WebaxRequest.__init__(self, uid)


class GetInnKppByPartyIdRequest(WebaxRequest):
    def __init__(self, party_id, uid):
        self.partyId = party_id
        WebaxRequest.__init__(self, uid)


class GetInnKppByRoute(WebaxRequest):
    def __init__(self, route_id, region, uid, release_date):
        self.routeId = int(route_id)
        self.releaseDate = str(release_date)
        self.region = region
        WebaxRequest.__init__(self, uid)


class WebaxRequestGetSourceSettings(WebaxRequest):
    def __init__(self, uid):
        WebaxRequest.__init__(self, uid)


class WebaxRequestGetAsuopSettings(WebaxRequest):
    def __init__(self, uid, companies):
        self.companies = companies
        WebaxRequest.__init__(self, uid)


class WebaxRequestGetToken(WebaxRequest):
    def __init__(self, uid, user_id):
        self.user_id = user_id
        WebaxRequest.__init__(self, uid)


class WebaxRequestGetFiscalApiSettings(WebaxRequest):
    def __init__(self, uid):
        WebaxRequest.__init__(self, uid)


class UpdateReviseDataSchema(Schema):
    additional_tickets = fields.List(fields.Nested(TicketSchema))
    missed_tickets = fields.List(fields.Nested(TicketSchema))
    additional_documents = fields.List(fields.Nested(DocumentSchema))
    missed_documents = fields.List(fields.Nested(DocumentSchema))
    inn = fields.String()
    kpp = fields.String()
    has_error = fields.Boolean()
    date = fields.Date()
    amount_tickets_db_cash = fields.Integer()
    amount_tickets_db_cashless = fields.Integer()
    amount_tickets_asuop_cash = fields.Integer()
    amount_tickets_asuop_cashless = fields.Integer()
    amount_documents_db_cash = fields.Integer()
    amount_documents_db_cashless = fields.Integer()
    amount_documents_ofd_cash = fields.Integer()
    amount_documents_ofd_cashless = fields.Integer()
    answer = fields.String()
    action = fields.String()
