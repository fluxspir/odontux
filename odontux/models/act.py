# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
from tables import payment_gesture_table 
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

class Gesture(Base):
    __tablename__ = 'gesture'
    id = Column(Integer, primary_key=True)
    specialty_id = Column(Integer, ForeignKey(Specialty.id), default=None)
    specialty = relationship("Specialty")
    name = Column(String, nullable=False, unique=True)
    alias = Column(String, default="", unique=True)
    code = Column(String, unique=True)
    color = Column(String, default="#000000")
    cotations = relationship('Cotation')
    healthcare_plans = association_proxy('cotations', 'healthcare_plan')
    
class Cotation(Base):
    __tablename__ = "cotation"
    id = Column(Integer, primary_key=True)
    gesture_id = Column(Integer, ForeignKey(Gesture.id), primary_key=True)
    healthcare_plan_id = Column(Integer, ForeignKey(HealthCarePlan.id), 
                                                            primary_key=True)
    price = Column(Numeric, nullable=True, default=0)
    active = Column(Boolean, default=True)
    gesture = relationship("Gesture")
    healthcare_plan = relationship('HealthCarePlan', backref="cotations")

class AppointmentGestureReference(Base):
    """ 
        anatomic_location_id = constants.ANATOMIC_LOCATION
    """
    __tablename__ = 'appointment_gesture_reference'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                            nullable=False)
    gesture_id = Column(Integer, ForeignKey(Gesture.id), nullable=False)
    anatomic_location = Column(Integer, nullable=False)
    healthcare_plan_id = Column(Integer, ForeignKey(HealthCarePlan.id))
    price = Column(Numeric, nullable=False)
    invoice_id = Column(String, default="")
    paid = Column(Boolean, default=False)
    gesture = relationship('Gesture')
