from marshmallow import Schema, fields

from schemas.InstallPlaceSchema import InstallPlaceSchema
from schemas.OfdSchema import OfdSchema
from schemas.CompanySchema import CompanySchema


class UpdateDictionariesSchema(Schema):
    companies = fields.List(fields.Nested(CompanySchema))
    ofds = fields.List(fields.Nested(OfdSchema))
    install_places = fields.List(fields.Nested(InstallPlaceSchema))
