from dataclasses import dataclass
from typing import List

from marshmallow import Schema, fields, validate, post_load
from marshmallow_enum import EnumField

from core.entities.Enums import Tax, Vat
from core.entities.entities import SourceSettings, Route, Division, CompanyAsuop, SourceType


@dataclass
class FiscalApiUser:
    id: str
    login: str
    password: str
    companies: List[str]


class SourceSettingsSchema(Schema):
    id = fields.String()
    type = EnumField(SourceType)
    address = fields.String()
    port = fields.Integer(strict=False, validate=validate.Range(min=0, max=65535))
    database_name = fields.String()
    login = fields.String()
    password = fields.String()
    timezone = fields.String()
    query_new_tickets = fields.String()
    query_revise = fields.String()
    query_by_id = fields.String()

    @post_load
    def make_model(self, data, **kwargs):
        return SourceSettings(**data)


class RouteSchema(Schema):
    route_num = fields.String()
    vat = EnumField(Vat)

    @post_load
    def make_model(self, data, **kwargs):
        return Route(**data)


class DivisionSchema(Schema):
    id = fields.Integer()
    source_id = fields.String()
    routes: fields.List(fields.Nested(RouteSchema))

    @post_load
    def make_model(self, data, **kwargs):
        return Division(**data)


class CompanyAsuopSchema(Schema):
    id = fields.String()
    inn = fields.String()
    kpp = fields.String()
    tax = EnumField(Tax)
    divisions = fields.List(fields.Nested(DivisionSchema))

    @post_load
    def make_model(self, data, **kwargs):
        return CompanyAsuop(**data)


class FiscalApiUserSchema(Schema):
    id = fields.String()
    login = fields.String(validate=validate.Length(max=20))
    password = fields.String(validate=validate.Length(max=20))
    companies = fields.List(fields.String())

    @post_load
    def make_model(self, data, **kwargs):
        return FiscalApiUser(**data)
