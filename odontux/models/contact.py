# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import sqlalchemy
import datetime

from tables import ( patient_mail_table, patient_phone_table ) 
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    street = Column(String, default="", nullable=False)
    street_number = Column(String, default="", nullable=False)
    building = Column(String, default="", nullable=False)
    complement = Column(String, default="", nullable=False)
    district = Column(String, default="", nullable=False)
    city = Column(String, default="", nullable=False)
    zip_code = Column(String, default="", nullable=False)
    state = Column(String, default="", nullable=False)
    country = Column(String, default="", nullable=False)
    update_date = Column(Date, default=func.current_date())


class Mail(Base):
    __tablename__ = 'mail'
    id = Column(Integer, primary_key=True)
    email = Column(String, default="")
    update_date = Column(Date, default=func.current_date())


class Phone(Base):
    __tablename__ = 'phone'
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    indicatif = Column(String, default="")
    area_code = Column(String, default="")
    number = Column(String, default="")
    update_date = Column(Date, default=func.current_date())


