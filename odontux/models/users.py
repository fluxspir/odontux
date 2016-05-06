# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import sqlalchemy
import datetime

from tables import (odontux_user_address_table, odontux_user_mail_table,
                    odontux_user_phone_table, dental_office_address_table,
                    dental_office_mail_table, dental_office_phone_table)

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref


class DentalOffice(Base):
    __tablename__ = 'dental_office'
    id = Column(Integer, primary_key=True)
    office_name = Column(String, default="")
    owner_lastname = Column(String, default="")
    owner_firstname = Column(String, default="")
    active = Column(Boolean, default=True)
    url = Column(String, default="")
    addresses = relationship("Address", secondary=dental_office_address_table,
                           backref="dental_office")
    phones = relationship("Phone", secondary=dental_office_phone_table,
                          backref="dental_office")
    mails = relationship("Mail", secondary=dental_office_mail_table,
                         backref="dental_office")
    patients = relationship("Patient", backref="office")


class OdontuxUser(Base):
    __tablename__ = 'odontux_user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    qualifications = Column(String, default="")
    registration = Column(String, default="")
    correspondence_name = Column(String, default="")
    addresses = relationship("Address", secondary=odontux_user_address_table,
                           backref="odontux_user")
    sex = Column(String, default="f")
    dob = Column(Date, default=datetime.date(1970, 1, 1))
    active = Column(Boolean, default=True)
    comments = Column(String, default="")
    mails = relationship("Mail", secondary=odontux_user_mail_table,
                        backref="odontux_user")
    phones = relationship("Phone", secondary=odontux_user_phone_table,
                         backref="odontux_user")
    avatar_id = Column(Integer, default=None)
    display_order = Column(Integer, default=None)
    modified_by = Column(Integer, default=None)
    creation_date = Column(Date, default=func.current_date())
    gnucash_url = Column(String, default="")
    dentist_supervisor_id = Column(Integer, ForeignKey('OdontuxUser'),
                                                            default=None)
    patients = relationship("Patient", backref="user")

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    value = Column(String)
