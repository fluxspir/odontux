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
from sqlalchemy.orm import relationship, backref


now = datetime.datetime.now()
today = datetime.date.today()


class Agenda(Base):
    __tablename__ = 'agenda'
    id = Column(Integer, primary_key=True)
    starttime = Column(DateTime, nullable=False)
    endtime = Column(DateTime, nullable=False)


class Appointment(Base):
    __tablename__ = 'appointment'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id),
                        nullable=False, default=1)
    agenda_id = Column(Integer, ForeignKey(Agenda.id), nullable=False)
    emergency = Column(Boolean, default=False)
    reason = Column(String, default="dentist didn't precise the appointment's "
                                    "reason.", nullable=False)
    diagnostic = Column(String)
    treatment = Column(String)
    prognostic = Column(String)
    advise = Column(String)
    next_appointment = Column(String)
    administrative_acts = relationship("AppointmentActReference",
                                       backref="appointment")
    ordonnance = relationship("Prescription", backref="appointment",
                              cascade="all, delete, delete-orphan")


class AppointmentMemo(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=1)
    appointment_id = Column(Integer, ForeignKey(Appointment.id))
    time_stamp = Column(DateTime, default=now)
    memo = Column(String)

