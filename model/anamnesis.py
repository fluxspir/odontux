# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import users, administration
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey


now = datetime.datetime.now()
today = datetime.date.today()


md_address_table = Table('md_address', Base.metadata,
Column('md_id', Integer, ForeignKey('md.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)



class MedecineDoctor(Base):
    __tablename__ = 'medecine_doctor'
    id = Column(Integer, primary_key=True)
    lastname = Column(String, nullable=False)
    firstname = Column(String)
    address = relationship("Address", secondary=md_address,
                           backref="md")
    city = Column(String)
    address = Column(String)
    phone = Column(String)
    mail = Column(String)
    patient = relationship("administration.Patient", backref="md")


class MedicalHistory(Base):
    __tablename__ = 'medical_history'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=1)
    icd10 = Column(String)
    disease = Column(String)
    disorder = Column(String)
    habitus = Column(String)
    treatment = Column(String)
    time_stamp = Column(Date, default=today)


class PastSurgeries(Base):
    __tablename__ = 'past_surgeries'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=1)
    surgery_type = Column(String)
    problem = Column(String)
    complication = Column(String)
    time_stamp = Column(Date, default=today)


class Allergies(Base):
    __tablename__ = 'allergies'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=1)
    drug = Column(String)
    metal = Column(String)
    food = Column(String)
    other = Column(String)
    reaction = Column(String)
    time_stamp = Column(Date, default=today)

