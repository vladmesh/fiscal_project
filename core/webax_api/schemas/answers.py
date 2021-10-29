from marshmallow import Schema, fields, post_load

from core.entities.entities import AsuopSettings
from core.entities.entity_schemas import CompanySchema, OfdSchema, InstallPlaceSchema, CashboxSchema, CompanyAsuopSchema
from core.webax_api.schemas.inner import SourceSettingsSchema


class UpdateDictionariesSchema(Schema):
    companies = fields.List(fields.Nested(CompanySchema))
    ofd_list = fields.List(fields.Nested(OfdSchema))
    install_places = fields.List(fields.Nested(InstallPlaceSchema))
    cashboxes = fields.List(fields.Nested(CashboxSchema))


class GetSourceSettingsSchema(Schema):
    source_settings = fields.List(fields.Nested(SourceSettingsSchema))


class GetAsuopSettingsSchema(Schema):
    companies = fields.List(fields.Nested(CompanyAsuopSchema))

    @post_load
    def make_model(self, data, **kwargs):
        return AsuopSettings(**data)
