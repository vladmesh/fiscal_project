from marshmallow import Schema, fields

from core.entities.entity_schemas import CompanySchema, OfdSchema, InstallPlaceSchema, CashboxSchema
from core.webax_api.schemas.inner import SourceSettingsSchema


class UpdateDictionariesSchema(Schema):
    companies = fields.List(fields.Nested(CompanySchema))
    ofd_list = fields.List(fields.Nested(OfdSchema))
    install_places = fields.List(fields.Nested(InstallPlaceSchema))
    cashboxes = fields.List(fields.Nested(CashboxSchema))


class GetSourceSettingsSchema(Schema):
    source_settings = fields.List(fields.Nested(SourceSettingsSchema))
