# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#
from meta import Base
import administration, schedule
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


class HeadEvent(Base):
    __tablename__ = 'head_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)

class NeckEvent(Base):
    __tablename__ = 'neck_event'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    comments = Column(String, default="")
    pic = Column(Boolean, default=False)
    x_ray = Column(Boolean, default=False)
    document = Column(Boolean, default=False)


