from marshmallow import Schema, fields, validate


class UserSchemaValidate(Schema):
    name = fields.Str(validate=[validate.Length(min=1, max=255), validate.Regexp(r'^[a-zA-Z\sÀ-ỹ]+$')])
    age = fields.Int(validate=validate.Range(min=0, max=100))
    address = fields.Str(validate=[validate.Length(min=1, max=255), validate.Regexp(r'^[a-zA-Z\sÀ-ỹ\0-9]+$')])
    phone_number = fields.Str(validate=[validate.Length(equal=10, error="Phone number must be exactly 10 digits."),
                                        validate.Regexp(r'^\d{10}$')])
    email = fields.Email()
    username = fields.Str(validate=[
        validate.Length(min=8, max=20, error="Username must be between 8 and 20 characters."),
        validate.Regexp(r'^(?=.*[a-z])(?=.*\d)[a-z\d]{8,20}$',
                        error="Check your Username again !!")
    ])

    password = fields.Str(validate=[
        validate.Length(min=8, max=20, error="Password must be between 8 and 20 characters."),
        validate.Regexp(r'^(?=.*[a-z])(?=.*\d)[a-z\d]{8,20}$',
                        error="Check your Password again !!")
    ])
    role = fields.Int(validate=validate.Range(min=1, max=4), error="Role's ID does not exist !!")
