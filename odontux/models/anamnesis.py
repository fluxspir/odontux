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
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


now = datetime.datetime.now()
today = datetime.date.today()


class MedicalHistory(Base):
    __tablename__ = 'medical_history'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=2)
    icd10 = Column(String, default="")
    disease = Column(String, default="")
    disorder = Column(String, default="")
    habitus = Column(String, default="")
    treatment = Column(String, default="")
    time_stamp = Column(Date, default=today)


class PastSurgeries(Base):
    __tablename__ = 'past_surgeries'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=2)
    surgery_type = Column(String, default="")
    problem = Column(String, default="")
    complication = Column(String, default="")
    time_stamp = Column(Date, default=today)


class Allergies(Base):
    __tablename__ = 'allergies'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=2)
    drug = Column(String, default="")
    metal = Column(String, default="")
    food = Column(String, default="")
    other = Column(String, default="")
    reaction = Column(String, default="")
    time_stamp = Column(Date, default=today)

