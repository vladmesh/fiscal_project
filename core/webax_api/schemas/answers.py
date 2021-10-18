from marshmallow import Schema, fields

from core.entities.entity_schemas import CompanySchema, OfdSchema, InstallPlaceSchema, CashboxSchema, RegionSchema


class UpdateDictionariesSchema(Schema):
    companies = fields.List(fields.Nested(CompanySchema))
    ofd_list = fields.List(fields.Nested(OfdSchema))
    install_places = fields.List(fields.Nested(InstallPlaceSchema))
    cashboxes = fields.List(fields.Nested(CashboxSchema))
    regions = fields.List(fields.Nested(RegionSchema))
