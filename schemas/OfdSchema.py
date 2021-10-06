from marshmallow import Schema, fields, validate, post_load

from core.entities.Ofd import Ofd


class OfdSchema(Schema):
    inn = fields.String(validate=validate.Length(10))
    domain = fields.String()
    name = fields.String()
    ip = fields.String(validate=validate.Regexp(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$'))
    port = fields.Integer(strict=False, validate=validate.Range(max=65535, min=1000))
    email = fields.Email()

    @post_load
    def make_ofd(self, data, **kwargs):
        return Ofd(**data)

