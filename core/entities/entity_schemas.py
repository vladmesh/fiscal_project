from marshmallow import Schema, validate, fields, post_load, ValidationError
from marshmallow_enum import EnumField

from core.entities.Enums import Vat, Tax, PaymentType, DocumentType
from core.entities.entities import Ofd, InstallPlace, Company, Cashbox,  Ticket, Document


class IntOrNone(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        if type(value) == int:
            return value
        raise ValidationError(f"В поле {attr} ожидалось значение типа int, получено значение типа {type(value)}")

    def _deserialize(self, value, attr, data, **kwargs):
        if value == "":
            return None
        try:
            return int(value)
        except ValueError as error:
            raise ValidationError(f"Не удалось преобразовать значение {value} в число.") from error


class EntitySchema(Schema):
    key = ''
    model_class = dict

    @post_load
    def make_model(self, data, **kwargs):
        return self.model_class(**data)


class OfdSchema(EntitySchema):
    key = 'ofd_list'
    model_class = Ofd
    inn = fields.String(validate=validate.Length(10))
    domain = fields.String()
    name = fields.String()
    ip = fields.String(validate=validate.Regexp(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$'))
    port = fields.Integer(strict=False, validate=validate.Range(max=65535, min=1000))
    email = fields.Email()


class InstallPlaceSchema(EntitySchema):
    key = 'install_places'
    model_class = InstallPlace
    id = fields.String()
    address = fields.String()


class CompanySchema(EntitySchema):
    key = 'companies'
    model_class = Company
    id = fields.String()
    inn = fields.String(validate=validate.Length(10), required=True)
    kpp = fields.String(validate=validate.Length(9), required=True)
    name = fields.String(validate=validate.Length(max=50))
    full_name = fields.String()
    timezone = fields.String(validate=validate.Length(max=30), required=True)
    payment_place = fields.String(validate=validate.Length(max=25))
    authorized_person_name = fields.String(validate=validate.Length(max=80))
    agent_agent = fields.Integer(validate=validate.Range(min=0, max=1))
    tax = fields.String(validate=validate.Length(min=3, max=9), required=True)
    provider_name = fields.String()
    provider_phone = fields.String()
    provider_inn = fields.String()
    additional_field_meaning = fields.String()
    additional_field_value = fields.String()


class CashboxSchema(EntitySchema):
    key = 'cashboxes'
    model_class = Cashbox
    ip = fields.String(validate=validate.Regexp(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$'))
    port = fields.Integer(strict=False, validate=validate.Range(min=1000, max=65535))
    fn_number = IntOrNone()
    location_id = fields.String()
    registry_number = fields.String()
    factory_number = IntOrNone()
    company_id = fields.String()
    ofd_inn = fields.String(validate=validate.Length(10))


class TicketSchema(EntitySchema):
    key = 'tickets'
    model_class = Ticket
    dbf_id = fields.Integer()
    asuop_id = fields.String()
    ticket_series = fields.String()
    ticket_number = fields.String()
    date_ins = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    date_trip = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    price = fields.Integer()
    vat = EnumField(Vat)
    tax = EnumField(Tax)
    company_id = fields.String()
    payment_type = EnumField(PaymentType)


class DocumentSchema(EntitySchema):
    key = 'documents'
    model_class = Document
    fiscal_storage_number = fields.Integer()
    fiscal_number = fields.Integer()
    fiscal_sign = fields.Integer()
    fiscal_date = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    ticket_id = fields.Integer()
    document_type = EnumField(DocumentType)
    session_num = fields.Integer()
    num_in_session = fields.Integer()
    company_id = fields.String()
    tax = EnumField(Tax)
    vat = EnumField(Vat)
    payment_type = EnumField(PaymentType)
    price = fields.Integer()
    cashbox_id = fields.Integer()
    additional_prop = fields.String(validate=validate.Length(max=16))


class CashboxListSchema(Schema):
    cashboxes = fields.List(fields.Nested(CashboxSchema))


class CompanyListSchema(Schema):
    companies = fields.Dict(fields.String, fields.Nested(CompanySchema))
