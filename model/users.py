# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


now = datetime.datetime.now()
today = datetime.date.today()

odontux_user_address_table = Table('user_address', Base.metadata,
Column('user_id', Integer, ForeignKey('user.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)

dental_office_address_table = Table('user_address', Base.metadata,
Column('user_id', Integer, ForeignKey('user.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)

class DentalOffice(Base):
    __tablename__ = 'dental_office'
    id = Column(Integer, primary_key=True)
    office_name = Column(String)
    dentist_lastname = Column(String)
    dentist_firstname = Column(String)
    address = relationship("Address", secondary=dental_office_address_table,
                           backref="dental_office")
    phone = Column(String)
    mail = Column(String)
    patients = relationship("Patient", backref="office")


class OdontuxUser(Base):
    __tablename__ = 'odontux_user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String)
    role = Column(String, nullable=False)
    title = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    qualifications = Column(String)
    registration = Column(String)
    correspondence_name = Column(String)
    address = relationship("Address", secondary=odontux_user_address_table,
                           backref="odontux_user")
    sex = Column(Boolean)
    dob = Column(Date)
    status = Column(Boolean, default=True)
    comments = Column(String)
    mail = Column(String)
    phone = Column(String)
    avatar_id = Column(Integer)
    display_order = Column(Integer)
    modified_by = Column(Integer)
    time_stamp = Column(Date, default=today)
    patients = relationship("Patient", backref="user")

