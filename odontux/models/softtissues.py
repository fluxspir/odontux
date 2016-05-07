# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#

from meta import Base
import administration
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import func

class SuperiorLipEvent(Base):
    __tablename__ = 'superior_lip'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class InferiorLipEvent(Base):
    __tablename__ = 'inferior_lip'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class LeftCheekEvent(Base):
    __tablename__ = 'left_cheek'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class RightCheekEvent(Base):
    __tablename__ = 'right_cheek'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class HardPalateEvent(Base):
    __tablename__ = 'hard_palate'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class SoftPalateEvent(Base):
    __tablename__ = 'soft_palate'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class TongueEvent(Base):
    __tablename__ = 'tongue'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class MouthBaseEvent(Base):
    __tablename__ = 'mouth_base'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())

