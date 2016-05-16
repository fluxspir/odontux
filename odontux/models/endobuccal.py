# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#

from meta import Base
import administration, schedule
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import func

class MouthEvent(Base):
    id = Column(Integer, primary_key=True)
    __tablename__ = 'mouth_event'
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)

class SuperiorLipEvent(Base):
    __tablename__ = 'superior_lip_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class InferiorLipEvent(Base):
    __tablename__ = 'inferior_lip_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class LeftCheekEvent(Base):
    __tablename__ = 'left_cheek_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class RightCheekEvent(Base):
    __tablename__ = 'right_cheek_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class HardPalateEvent(Base):
    __tablename__ = 'hard_palate_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class SoftPalateEvent(Base):
    __tablename__ = 'soft_palate_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class TongueEvent(Base):
    __tablename__ = 'tongue_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


class MouthBaseEvent(Base):
    __tablename__ = 'mouth_base_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)

class UvulaEvent(Base):
    __tablename__ = 'uvula_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                    nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    name = Column(String, default="")
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)

