from marshmallow import Schema, fields


class RoleSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    age = fields.Int()
    address = fields.Str()
    phone_number = fields.Str()
    email = fields.Str()
    role = fields.Nested(RoleSchema)
    username = fields.Str()
    created_at = fields.Str()
    updated_at = fields.Str()
    created_by = fields.Str()
    updated_by = fields.Str()
