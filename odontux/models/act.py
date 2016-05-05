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
from sqlalchemy.ext.associationproxy import association_proxy


class Specialty(Base):
    __tablename__ = 'specialty'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    color = Column(String, default="#000000")

class HealthCarePlan(Base):
    __tablename__ = "healthcare_plan"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

class ActType(Base):
    __tablename__ = 'act_type'
    id = Column(Integer, primary_key=True)
    specialty_id = Column(Integer, ForeignKey(Specialty.id), default=None)
    specialty = relationship("Specialty")
    name = Column(String, nullable=False)
    alias = Column(String, default="")
    code = Column(String, unique=True)
    color = Column(String, default="#000000")
    healthcare_plans = association_proxy('cotations', 'healthcare_plan')
    
class Cotation(Base):
    __tablename__ = "cotation"
    id = Column(Integer, primary_key=True)
    acttype_id = Column(Integer, ForeignKey(ActType.id), primary_key=True)
    healthcare_plan_id = Column(Integer, ForeignKey(HealthCarePlan.id), 
                                                            primary_key=True)
    price = Column(Numeric, nullable=True, default=0)
    active = Column(Boolean, default=True)

    acttype = relationship("ActType", backref=backref("cotations"))
    healthcare_plan = relationship('HealthCarePlan', backref="cotations")

class AppointmentActReference(Base):
    __tablename__ = 'appointment_act_reference'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                            nullable=False)
    act_id = Column(Integer, ForeignKey(ActType.id), nullable=False)
    tooth_id = Column(Integer, ForeignKey(teeth.Tooth.id))
    healthcare_plan_id = Column(Integer, ForeignKey(HealthCarePlan.id))
    code = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    invoice_id = Column(String, default="")
    paid = Column(Boolean, default=False)
