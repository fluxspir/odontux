# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
from tables import material_category_gesture_table
import schedule, headneck, teeth, users
import sqlalchemy
from sqlalchemy import ( Table, Column, Integer, String, Numeric, Boolean, 
                            Interval)
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

import datetime

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
    """ a Gesture is the common name of the global act
        that can be one or more ClinicAct
        A gesture as a set of materials that may be used in
        ones of the clinic acts that compose the gesture 
    """
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
    materials = relationship('MaterialCategory', 
                            secondary=material_category_gesture_table)
   
class ClinicGesture(Base):
    """ a ClinicGesture is define by its material used, is mean time, 
        and, as a consequence, its cost."""
    __tablename__ = 'clinic_gesture'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    duration = Column(Interval, default=datetime.timedelta(seconds= 5 * 60))
    materials = relationship('MaterialCategoryClinicGestureReference',
                    cascade="all, delete, delete-orphan", backref="gesture")
    is_daily = Column(Boolean, default=False)
    is_appointmently = Column(Boolean, default=False)

class Cotation(Base):
    """
    """
    __tablename__ = "cotation"
    id = Column(Integer, primary_key=True)
    gesture_id = Column(Integer, ForeignKey(Gesture.id), nullable=False)
    healthcare_plan_id = Column(Integer, ForeignKey(HealthCarePlan.id), 
                                                            nullable=False)
    price = Column(Numeric, nullable=True, default=0)
    active = Column(Boolean, default=True)
    gesture = relationship("Gesture")
    healthcare_plan = relationship('HealthCarePlan', backref="cotations")
    clinic_gestures = relationship('ClinicGestureCotationReference', 
                                cascade="all, delete, delete-orphan",
                                backref="cotations")
    gests = association_proxy('clinic_gestures', 'clinic_gesture')

class ClinicGestureCotationReference(Base):
    __tablename__ = "clinic_gesture_cotation_reference"
    id = Column(Integer, primary_key=True)
    clinic_gesture_id = Column(Integer, ForeignKey(ClinicGesture.id), 
                                                            nullable=False)
    cotation_id = Column(Integer, ForeignKey(Cotation.id), nullable=False)
    official_cotation = Column(Boolean, default=False)
    appears_on_appointment_resume = Column(Boolean, default=False)
    clinic_gesture = relationship('ClinicGesture') 
    appointment_number = Column(Integer, default=0)
    appointment_sequence = Column(Integer, default=0)

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
    is_paid = Column(Boolean, default=False)
    gesture = relationship('Gesture')

class HealthCarePlanUserReference(Base):
    """ """
    __tablename__ = 'healthcare_plan_user_reference'
    id = Column(Integer, primary_key=True)
    healthcare_plan_id = Column(Integer, ForeignKey(HealthCarePlan.id),
                                                        nullable=False)
    user_id = Column(Integer, ForeignKey(users.OdontuxUser.id), nullable=False)
    healthcare_plan = relationship('HealthCarePlan')
    hour_fees = Column(Numeric, nullable=False)
