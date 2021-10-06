from marshmallow import Schema, fields, validate, post_load, ValidationError

from core.entities import Cashbox


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


class CashboxSchema(Schema):
    ip = fields.String(validate=validate.Regexp(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$'))
    port = fields.Integer(strict=False, validate=validate.Range(min=1000, max=65535))
    fn_number = IntOrNone()
    location_id = fields.String()
    registry_number = fields.String()
    factory_number = IntOrNone()
    company_id = fields.String()
    ofd_inn = fields.String(validate=validate.Length(10))

    @post_load
    def make_cashbox(self, data, **kwargs):
        return Cashbox(**data)


class CashboxListSchema(Schema):
    cashboxes = fields.List(fields.Nested(CashboxSchema))
