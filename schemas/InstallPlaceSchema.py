from marshmallow import Schema, fields, post_load

from core.entities.InstallPlace import InstallPlace


class InstallPlaceSchema(Schema):
    id = fields.String()
    address = fields.String()

    @post_load
    def make_installPlace(self, data, **kwargs):
        return InstallPlace(**data)

