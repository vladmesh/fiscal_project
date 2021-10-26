import abc
from dataclasses import dataclass
from typing import Optional

from marshmallow import Schema, fields, post_load, validate


@dataclass
class CashboxCommandRequest(abc.ABC):
    cashbox_id: int
    company_id: str
    ip: str
    port: int


@dataclass
class GetCashboxDataRequest(CashboxCommandRequest):
    pass


class CashboxCommandRequestSchema(Schema):
    cashbox_id = fields.Integer()
    company_id = fields.String()
    ip = fields.String()
    port = fields.Integer()


class GetCashboxDataRequestSchema(CashboxCommandRequestSchema):
    @post_load
    def make_model(self, data, **kwargs):
        return GetCashboxDataRequest(**data)


@dataclass
class CashboxRegisterRequest(CashboxCommandRequest):
    company_name: str
    company_authorized_person_name: str
    company_payment_place: str
    install_place_address: str
    ofd_inn: str
    ofd_name: str
    ofd_email: str
    company_agent_agent: bool
    company_inn: str
    company_tax: int
    register_type: int
    cashbox_registry_number: str
    cashbox_auto_device_number: Optional[str]
    reason: Optional[int]


class CashboxRegisterRequestSchema(CashboxCommandRequestSchema):
    company_name = fields.String()
    company_authorized_person_name = fields.String()
    company_payment_place = fields.String()
    install_place_address = fields.String()
    ofd_inn = fields.String()
    ofd_name = fields.String()
    ofd_email = fields.String()
    company_agent_agent = fields.String()
    company_inn = fields.String()
    company_tax = fields.Integer()
    register_type = fields.Integer()
    cashbox_registry_number = fields.String()
    cashbox_auto_device_number = fields.String(allow_none=True)
    reason = fields.Integer(allow_none=True)

    @post_load
    def make_model(self, data, **kwargs):
        return CashboxRegisterRequest(**data)


class CloseCashboxRequestSchema(CashboxCommandRequestSchema):
    pass
