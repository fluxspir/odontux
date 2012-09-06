# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#
from meta import Base
import users, anamnesis
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


now = datetime.datetime.now()
today = datetime.date.today()


class City(Base):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True)
    city = Column(String, default="")
    postal_code = Column(String, default="")


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    addr = Column(String)
    building = Column(String)
    city_id = Column(Integer, ForeignKey(City.id)
    county = Column(String, default="")
    country = Column(String, default="France")
    update_date = Column(Date, default=today())


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    lastname = Column(String, nullable=False)
    firstname = Column(String)
    qualifications = Column(String)
    preferred_name = Column(String)
    correspondence_name = Column(String)
    address = relationship("Address", secondary=patient_address_table,
                           backref="patient")
    sex = Column(Boolean)
    dob = Column(Date, default="19700101")                  # date of birth
    job = Column(String)
    phone = Column(String)
    mail = Column(String)
    inactive = Column(Boolean, default=False)
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id), default=1)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=1)
    gen_doc_id = Column(Integer, ForeignKey(anamnesis.MedecineDoctor.id))
    time_stamp = Column(Date, default=today)
    head = relationship("Head", uselist=False, backref="patient")
    neck = relationship("Neck", uselist=False, backref="patient") 
    mouth = relationship("Mouth", uselist=False, backref="patient") 
    appointments = relationship("Appointment", backref="patient")

    def age(self):
        return (
            today.year - self.dob.year
             - int((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def is_birthday(self):
        if today.month == self.dob.month and today.day == self.dob.day:
            return True
        else:
            return False

