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
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref


class Appointment(Base):
    __tablename__ = 'appointment'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id),
                        nullable=False)
    dental_unit_id = Column(Integer, ForeignKey(users.DentalUnit.id),
                        nullable=False)
    agenda = relationship("Agenda", uselist=False, backref="appointment", 
                           cascade="all, delete, delete-orphan")
    emergency = Column(Boolean, default=False)
    reason = Column(String, default="", nullable=False)
    diagnostic = Column(String, default="")
    treatment = Column(String, default="")
    prognostic = Column(String, default="")
    advise = Column(String, default="")
    next_appointment = Column(String, default="")
    absent = Column(Boolean, default=False)
    excuse = Column(String, default="")
    dentist = relationship('users.OdontuxUser')
    administrative_gestures = relationship("AppointmentGestureReference",
                                       backref="appointment",
                                       cascade="all, delete, delete-orphan")
    ordonnance = relationship("Prescription", backref="appointment",
                              cascade="all, delete, delete-orphan")
    memo = relationship("AppointmentMemo", backref="appointment",
                         cascade="all, delete, delete-orphan")
    events = relationship("Event",
                        cascade="all, delete, delete-orphan")
    materiovigilance = relationship("traceability.MaterioVigilance", 
                                                        backref="appointments")

class Agenda(Base):
    __tablename__ = 'agenda'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey(Appointment.id))
    dental_unit_id = Column(Integer, ForeignKey(users.DentalUnit.id),
                                                                nullable=False)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id),
                                                                nullable=False)
    date_taker_id = Column(Integer, ForeignKey(users.OdontuxUser.id),
                                                                nullable=False)
    starttime = Column(DateTime, nullable=False)
    endtime = Column(DateTime, nullable=False)
    comment = Column(String)

class AppointmentMemo(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
    appointment_id = Column(Integer, ForeignKey(Appointment.id))
    time_stamp = Column(DateTime, default=func.now())
    memo = Column(String, default="")

