# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
from tables import payment_act_table
import schedule, headneck, teeth
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Numeric, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref


class Specialty(Base):
    __tablename__ = 'specialty'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, default="#000000")


class ActType(Base):
    __tablename__ = 'act_type'
    id = Column(Integer, primary_key=True)
    specialty_id = Column(Integer, ForeignKey(Specialty.id), default=None)
    name = Column(String, nullable=False)
    alias = Column(String, default="")
    code = Column(String, unique=True)
    color = Column(String, default="#000000")


class AppointmentActReference(Base):
    __tablename__ = 'appointment_act_reference'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                            nullable=False)
    act_id = Column(Integer, ForeignKey(ActType.id), nullable=False)
    tooth_id = Column(Integer, ForeignKey(teeth.Tooth.id))
    code = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    invoice_id = Column(String, default="")
    paid = Column(Boolean, default=False)
