# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/26
# v0.5
# Licence BSD
#

from gettext import gettext as _
from wtforms import widgets, Field
from wtforms import (Form, IntegerField, TextField, PasswordField,
                    SelectField, BooleanField, TextAreaField,
                    validators)

def upper_field(value):
    if value:
        return value.upper()
    return value

def lower_field(value):
    if value:
        return value.lower()
    return value

def title_field(value):
    if value:
        return value.title()
    return value


class ColorInput(widgets.TextInput):
    input_type = "color"

class ColorField(Field):
    widget = ColorInput()
    def _value(self):
        if self.data:
            return self.data


class EmailInput(widgets.TextInput):
    input_type = "email"

class EmailField(Field):
    widget = EmailInput()
    def _value(self):
        if self.data:
            return self.data


class TelInput(widgets.TextInput):
    input_type = "tel"

class TelField(Field):
    widget = TelInput()
    def _value(self):
        if self.data:
            return self.data


class DateInput(widgets.TextInput):
    input_type = "date"

class DateField(Field):
    widget = DateInput()
    def _value(self):
        if self.data:
            return self.data
            



class PhoneForm(Form):
    phonename = TextField('phonename', validators=[validators.Optional()])
    phonenum = TelField('phonenum', [validators.Optional()])

class AddressForm(Form):
    address_id = TextField('address_id')
    street = TextField('street', validators=[validators.Optional(),
                                 validators.Length(max=50, message=_("""Number
                                 and street must be less than 50 characters 
                                 please"""))])
    building = TextField('building', validators=[validators.Optional(), 
                                     validators.Length(max=50)])
    city = TextField('city', validators=[validators.Optional(),
                             validators.Length(max=25,
                             message=_("City's name"))], 
                             filters=[title_field])
    postal_code = IntegerField('postal_code', [validators.Optional()])
    county = TextField('county', validators=[validators.Optional(), 
                                  validators.Length(max=15)], 
                                 filters=[title_field])
    country = TextField('country', validators=[validators.Optional(),
                                   validators.Length(max=15)],
                                   filters=[title_field])

class MailForm(Form):
    email = EmailField('email', validators=[validators.Optional(),
                                      validators.Email()],
                                      filters=[lower_field])

