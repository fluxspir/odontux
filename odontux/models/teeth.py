# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
from tables import teeth_event_file_table
import users, headneck, schedule, administration
import sqlalchemy
try:
    from odontux import constants
except ImportError:
    import constants

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


class Arcade(Base):
    """ """
    __tablename__ = 'arcade'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                            nullable=False)
    location = Column(Integer, nullable=False)

class Quadrant(Base):
    """ """
    __tablename__ = 'quadrant'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                            nullable=False)
    location = Column(Integer, nullable=False)

class Sextant(Base):
    """ """
    __tablename__ = 'maxillar_arcade'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                            nullable=False)
    location = Column(Integer, nullable=False)

class Tooth(Base):
    """
    codeame link to constants.TOOTH
    The actual tooth state (see constant.TOOTH_STATES)
    We may put it under surveillance.
    """
    __tablename__ = 'tooth'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    codename = Column(Integer, nullable=False)
    state = Column(Integer, default=0, nullable=True)
    surveillance = Column(Boolean, default=False)
    #patient = relationship('Patient', backref="teeth")

class Gum(Base):
    """
    """
    __tablename__ = "gum"
    id = Column(Integer, ForeignKey(Tooth.id), primary_key=True)
    state = Column(Integer, default=0)
    bleeding = Column(Boolean)
    tooth = relationship('Tooth', backref='periodonte')

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
    comment = Column(String, default="")
    color = Column(String, default="")
    files = relationship("Files", secondary=teeth_event_file_table)
    location = Column(Integer, nullable=False)
    tooth = relationship('Tooth', backref="events")
    appointment = relationship('Appointment')

    __mapper_args__ = {
        'polymorphic_identity': 'event',
        'polymorphic_on': location
    }

class PeriodontalEvent(Event):
    """
        perio_location : constants.PERIODONTAL_LOCATIONS 
    """
    __tablename__ = "periodontal_event"
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    furcation = Column(Integer, default=0)
    recession = Column(Integer, default=0)
    pocket_depth = Column(Integer, default=0)
    is_mesio_buccal = Column(Boolean, default=False)
    is_buccal = Column(Boolean, default=False)
    is_disto_buccal = Column(Boolean, default=False)
    is_disto_lingual = Column(Boolean, default=False)
    is_lingual = Column(Boolean, default=False)
    is_mesio_lingual = Column(Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_PERIODONTAL
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
    Occurs on one or more faces : constants.CROWN_SIDES
    We may add comments
    We may use a color-code for what happened
    For the pics, see "toothevent"
    """
    __tablename__ = 'crown_event'
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    state = Column(Integer, nullable=False) 
    is_occlusal = Column(Boolean, default=False)
    is_buccal = Column(Boolean, default=False)
    is_lingual = Column(Boolean, default=False)
    is_mesial = Column(Boolean, default=False)
    is_distal = Column(Boolean, default=False)
    tooth_shade = Column(String, default=None)

    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_CROWN
    }

class RootCanalEvent(Event):
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
    __tablename__ = 'root_canal_event'
    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    state = Column(Integer, nullable=False) 
    is_central = Column(Boolean, default=False)
    is_buccal = Column(Boolean, default=False)
    is_lingual = Column(Boolean, default=False)
    is_mesial = Column(Boolean, default=False)
    is_distal = Column(Boolean, default=False)
    is_mesio_buccal = Column(Boolean, default=False)
    is_disto_buccal = Column(Boolean, default=False)
    is_mesio_lingual = Column(Boolean, default=False)
    is_disto_lingual = Column(Boolean, default=False)
    is_mesio_buccal_2 = Column(Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.TOOTH_EVENT_LOCATION_ROOT
    }
