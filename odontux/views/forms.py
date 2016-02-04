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

from flask import session, request

from odontux import constants
from odontux import gnucash_handler
from odontux.models import (meta,
                            administration,
                            md,
                            users,
                            assets
                            )

address_fields = ["street", "building", "complement", "city", "zip_code", 
                    "county", "country" ]
phone_fields = [ ("phonename", "name"), ("phoneindicatif", "indicatif"), 
                ("phoneareacode", "area_code"), ("phonenum", "number") ]
mail_fields = [ "email" ]

def get_title_choice_list():
    return [ ( "Mr", _("Mr") ), ("Mme", _("Mme") ), ( "Mlle", _("Mlle")),
             ( "Dr", _("Dr") ), ( "Pr", _("Pr")) ] 



# create filter for fields of wtforms
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

# Create new wtforms Fields
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

class TimeInput(widgets.TextInput):
    input_type = "time"

class TimeField(Field):
    widget = TimeInput()
    def _value(self):
        if self.data:
            return self.data


# Generic Forms
class PhoneForm(Form):
    phonename = TextField(_('phonename'), validators=[validators.Optional()])
    phoneindicatif = TextField(_('country\' indicatif'),
                                [validators.Optional()])
    phoneareacode = TextField(_('area_code'), [validators.Optional()])
    phonenum = TextField(_('phonenum'), [validators.Optional()])

class AddressForm(Form):
    address_id = TextField('address_id')
    street = TextField(_('street'), validators=[validators.Optional(),
                                 validators.Length(max=50, message=_("""Number
                                 and street must be less than 50 characters 
                                 please"""))])
    complement = TextField(_('complement'), [validators.Optional()])
    building = TextField(_('building'), validators=[validators.Optional(), 
                                     validators.Length(max=50)])
    city = TextField(_('city'), validators=[validators.Optional(),
                             validators.Length(max=25,
                             message=_("City's name"))], 
                             filters=[title_field])
    zip_code = TextField(_('zip_code'))
    county = TextField(_('county'), validators=[validators.Optional(), 
                                  validators.Length(max=15)], 
                                 filters=[title_field])
    country = TextField(_('country'), validators=[validators.Optional(),
                                   validators.Length(max=15)],
                                   filters=[title_field])

class MailForm(Form):
    email = TextField(_('email'), validators=[validators.Optional(),
                                      validators.Email()],
                                      filters=[lower_field])

# verify the user is allowed to update
def _check_body_perm(body, body_type):
    """ Return True if the odontux user trying to perform an
        update on administrative data is allowed.
        Otherwise, return False
    """
    # Only ADMIN (and own body) may update infos
    if body_type == 'user':
        if session['role'] != constants.ROLE_ADMIN \
        and session['username'] != body.username:
            return False
    # Only ADMIN may update dental_office infos        
    elif body_type == 'dental_office':
        if session['role'] != constants.ROLE_ADMIN:
            return False
    # DENTISTS, NURSE, ASSISTANT, SECRETARIES can make update in 
    # administration patient's files.
    elif body_type == 'md':
        if session['role'] == constants.ROLE_ADMIN:
            return False
    elif body_type == 'patient':
        if session['role'] == constants.ROLE_ADMIN:
            return False
    elif body_type == 'provider':
        if session['role'] == constants.ROLE_ADMIN:
            return False
    else:
        raise Exception(_("Unknown body type"))
        return False
    return True

# Get body information in the database
def _get_body(body_id, body_type):
    """ Return sqlalchemy object representing the person in database
        we want to update ; could be a patient, an OdontuxUser, a
        medecine doctor.
    """
    if body_type == 'user':
        body = meta.session.query(users.OdontuxUser).filter\
            (users.OdontuxUser.id == body_id).one()
    elif body_type == 'md':
        body = meta.session.query(md.MedecineDoctor).filter\
            (md.MedecineDoctor.id == body_id).one()
    elif body_type == 'patient':
        body = meta.session.query(administration.Patient).filter\
            (administration.Patient.id == body_id).one()
    elif body_type == "dental_office":
        body = meta.session.query(users.DentalOffice).filter\
            (users.DentalOffice.id == body_id).one()
    elif body_type == "provider":
        body = meta.session.query(assets.AssetProvider).filter(
            assets.AssetProvider.id == body_id).one()
    else:
        raise Exception(_("please specify known body_type"))
    return body

def update_body_address(body_id, body_type):
    """ An address exists for body in database but is erroneus (typo, wrong 
        town, anything) : this function will update the address to right thing.
    """
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = AddressForm(request.form)
    address_index = int(request.form["address_index"])
    if request.method == 'POST' and form.validate():
        for f in address_fields:
            if body_type == "patient":
                setattr(body.family.addresses[address_index], f, 
                        getattr(form, f).data)
                meta.session.commit()
                # update address in gnucash for patient.
                comptability = gnucash_handler.GnuCashCustomer(body.id,
                                                 body.dentist_id)
                customer = comptability.update_customer()
            else:
                setattr(body.addresses[address_index], f, 
                        getattr(form, f).data)
                meta.session.commit()
        return True
        
def add_body_address(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = AddressForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in address_fields}
        if body_type == "patient":
            body.family.addresses.append(administration.Address(**args))
            meta.session.commit()
            # in gnucash
            comptability = gnucash_handler.GnuCashCustomer(body.id,
                                                          body.dentist_id)
            customer = comptability.update_customer()
        else:
            body.addresses.append(administration.Address(**args))
            meta.session.commit()
        return True

def delete_body_address(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = AddressForm(request.form)
    address_id = int(request.form['address_id'])
    if request.method == 'POST' and form.validate():
        address = meta.session.query(administration.Address)\
                .filter(administration.Address.id == address_id).one()
        meta.session.delete(address)
        meta.session.commit()
        return True

def update_body_phone(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = PhoneForm(request.form)
    phone_index = int(request.form["phone_index"])
    if request.method == 'POST' and form.validate():
        for (f,g) in phone_fields:
            setattr(body.phones[phone_index], g, getattr(form, f).data)
        meta.session.commit()
        return True 
    

def add_body_phone(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = PhoneForm(request.form)
    if request.method == 'POST' and form.validate():
        args = { g: getattr(form, f).data for f, g in phone_fields }
        body.phones.append(administration.Phone(**args))
        meta.session.commit()
        return True

def delete_body_phone(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = PhoneForm(request.form)
    phone_id = int(request.form["phone_id"])
    if request.method == 'POST' and form.validate():
        try:
#            phone = (
#                meta.session.query(administration.Phone)
#                    .filter(and_(
#                        and_(
#                            administration.Phone.name == form.phonename.data,
#                            administration.Phone.number == form.phonenum.data
#                        ),
#                        administration.Phone.id == phone_id)
#                    )
#                ).one()
            phone = meta.session.query(administration.Phone)\
                    .filter(administration.Phone.id == phone_id).one()
            meta.session.delete(phone)
            meta.session.commit()
            return True
        except:
            raise Exception("phone delete problem")

def update_body_mail(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = MailForm(request.form)
    mail_index = int(request.form["mail_index"])
    if request.method == 'POST' and form.validate():
        for f in mail_fields:
            setattr(body.mails[mail_index], f, getattr(form, f).data)
        meta.session.commit()
        return True

def add_body_mail(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = MailForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in mail_fields }
        body.mails.append(administration.Mail(**(args)))
        meta.session.commit()
        return True

def delete_body_mail(body_id, body_type):
    body = _get_body(body_id, body_type)
    if not _check_body_perm(body, body_type):
        return False
    form = MailForm(request.form)
    mail_id = int(request.form['mail_id'])
    if request.method == 'POST' and form.validate():
        mail = meta.session.query(administration.Mail)\
                .filter(administration.Mail.id == mail_id).one()
        meta.session.delete(mail)
        meta.session.commit()
        return True
