# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import users, administration, headneck, schedule
import sqlalchemy
from odontux import constants

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref

class Tooth(Base):
    """
    A tooth has to have a name, the choice is free to name it whatever you want
    Name it in constants.
    The actual tooth state (see constant.py.TOOTH_STATES)
    We may put it under surveillance.
    """
    __tablename__ = 'tooth'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    name = Column(String, nullable=False)
    state = Column(Integer, default=0, nullable=True)
    surveillance = Column(Boolean, default=False)
    patient = relationship('Patient', backref="teeth")

class Periodonte(Base):
    """
    """
    __tablename__ = "periodonte"
    id = Column(Integer, ForeignKey(Tooth.id), primary_key=True)
    tooth = relationship('Tooth', backref='periodonte')
    state = Column(Integer, default=0)
    bleeding = Column(Boolean)

class Event(Base):
    """
    location : constants.TOOTH_EVENT_LOCATIONS
    """
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    tooth_id = Column(Integer, ForeignKey(Tooth.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                nullable=False)
    description = Column(String)
    comments = Column(String, default="")
    color = Column(String, default="")
    pic = Column(String, default="")
    location = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'event',
        'polymorphic_on': location
    }

class PeriodonteEvent(Event):
    """
        perio_location : constants.PERIODONTAL_LOCATIONS 
    """
    __tablename__ = "periodonte_event"
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    perio_location = Column(Integer, default=0)
    furcation = Column(Integer, default=0)
    recession = Column(Integer, default=0)
    pocket_depth = Column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_PERIODONTE
    }

class ToothEvent(Event):
    """
    A tooth event is an event we can't really class neither as a crown event,
    nor as a root event.
    Event that can occur to a tooth: constants.TOOTH_STATES
    We may add random comments
    We may add path to pics ; maybe just tell "True/False", if the path is
    obvious. Still to define
    """
    __tablename__ = 'tooth_event'
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    state = Column(Integer, nullable=False) 
    
    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_TOOTH
    }

class CrownEvent(Event):
    """
    Crown events :
    Must occur to a tooth (tooth_id)
    Are noticed while an appointment (appointment_id)
    Occurs on one or more faces :
        * o : Occlusal
        * m : Mesial
        * d : Distal
        * v/b : Vestibular / Buccal
        * l/p : Lingual / Palatal
        * a : All (usually, when the tooth is crowned)
    A crown is either :
        * s : sane
        * x : sealed
        * c : crowned
        * b : bridge
        * o : obturation
        * d : decayed
    We may add comments
    We may use a color-code for what happened
    For the pics, see "toothevent"
    """
    __tablename__ = 'crown_event'
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    state = Column(Integer, nullable=False) 
    side = Column(String, nullable=False)
    tooth_shade = Column(String, default=None)

    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_CROWN
    }

class RootEvent(Base):
    """
    Root events :
    Must occur to a tooth (tooth_id)
    Are noticed while on an appointment (appointment_id)
    Occurs on root : constants.ROOT_CANALS
    A root canal may be either contants.ROOT_STATES
    We may add comments
    We may use a color-code for what happened
    For the pics, see "toothevent"
    """
    __tablename__ = 'root_event'
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    state = Column(Integer, nullable=False) 
    root = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_ROOT
    }
