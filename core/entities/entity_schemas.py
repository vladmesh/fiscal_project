import abc

from marshmallow import Schema, validate, fields, post_load, ValidationError

from core.entities.entities import Ofd, InstallPlace, Company, Cashbox


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
    inn = fields.String(validate=validate.Length(10))
    kpp = fields.String(validate=validate.Length(9))
    name = fields.String(validate=validate.Length(max=50))
    full_name = fields.String()
    region = fields.String(validate=validate.Length(max=4))
    payment_place = fields.String(validate=validate.Length(max=25))
    authorized_person_name = fields.String(validate=validate.Length(max=80))
    agent_agent = fields.Integer(validate=validate.Range(min=0, max=1))
    tax = fields.Integer(validate=validate.Range(min=0, max=2))
    provider_name = fields.String()
    provider_phone = fields.String()
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
