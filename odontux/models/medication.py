# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import users, administration, schedule, documents
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import func

class DrugFamily(Base):
    __tablename__ = 'drug_family'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class DrugPrescribed(Base):
    __tablename__ = 'drug_prescribed'
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey(DrugFamily.id), nullable=False)
    alias = Column(String, unique=True, nullable=False)
    molecule = Column(String, nullable=False)
    packaging = Column(String, nullable=False)
    posologia = Column(String, nullable=False)
    dayssupply = Column(String, nullable=False)
    comments = Column(String, default="")
    special = Column(Boolean, default=False)
    family = relationship('DrugFamily', backref='drugs')

class Prescription(Base):
    __tablename__ = 'prescription'
    id = Column(Integer, primary_key=True)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), 
                        nullable=False)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id))
    file_id = Column(Integer, ForeignKey(documents.Files.id), nullable=False)
    time_stamp = Column(DateTime, nullable=False, default=func.now())
    prescription_file = relationship('documents.Files')

class PrescribedDrugReference(Base):
    __tablename__ = 'prescribed_drug_reference'
    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey(Prescription.id),
                             nullable=False)
    drug_id = Column(Integer, ForeignKey(DrugPrescribed.id), nullable=False)
    position = Column(Integer, nullable=False)
