# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import users, administration, schedule
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import func


class DrugPrescribed(Base):
    __tablename__ = 'drug_prescribed'
    id = Column(Integer, primary_key=True)
    alias = Column(String, unique=True, nullable=False)
    molecule = Column(String, nullable=False)
    packaging = Column(String, nullable=False)
    posologia = Column(String, nullable=False)
    dayssupply = Column(String, nullable=False)
    comments = Column(String, default="")
    special = Column(Boolean, default=False)

class Prescription(Base):
    __tablename__ = 'prescription'
    id = Column(Integer, primary_key=True)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), 
                        nullable=False)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id))
    time_stamp = Column(Date, nullable=False, default=func.current_date())


class PrescribedDrugReference(Base):
    __tablename__ = 'prescribed_drug_reference'
    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey(Prescription.id),
                             nullable=False)
    drug_id = Column(Integer, ForeignKey(DrugPrescribed.id), nullable=False)

