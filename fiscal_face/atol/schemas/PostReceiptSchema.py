from marshmallow import Schema, fields, validate


class Service(Schema):
    callback_url = fields.String(validate=validate.Regexp(r"^http(s?)\:\/\/[0-9a-zA-Zа-яА-Я]"
                                                          r"([-.\w]*[0-9a-zA-Zа-яА-Я])*(:(0-9)*)"
                                                          r"*(\/?)([azA-Z0-9а-яА-Я\-\.\?\,\'\/\\\+&=%\$#_]*)?$"))


class PostReceiptSchema(Schema):
    timestamp = fields.DateTime(format="%d.%m.%Y H%:%M:%S")
    external_id = fields.String(validate=validate.Length(max=128))
