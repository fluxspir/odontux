# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import users, administration, headneck, schedule
import sqlalchemy

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey

class Tooth(Base):
    """
    A tooth has to be in a mouth ;
    A tooth has to have a name, the choice is free to name it whatever you want
    A tooth is either :
        * None : The tooth never made speak from her.
        * s : sane ; a root-infected tooth may appear sane !
        * x : sealing
        * o : obturation
        * c : crowned
        * d : decayed
        * p : place
        * m : mobility
        * f : fracture
        * a : absent
        * b : bridge
        * r : resin (prosthetic mobile)
        * I : implant
    We may put it under surveillance.
    """
    __tablename__ = 'tooth'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id), nullable=False)
    name = Column(String, nullable=False)
    state = Column(String, default="")
    surveillance = Column(Boolean, default=False)

class Event(Base):
    """ """
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    tooth_id = Column(Integer, ForeignKey(Tooth.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                nullable=False)
    location = Column(Integer, nullable=False)
    color = Column(String, default="")
    pic = Column(String, default="")
    comments = Column(String, default="")

class ToothEvent(Base):
    """
    A tooth event is an event we can't really class neither as a crown event,
    nor as a root event.
    Event that can occur to a tooth:
        * sane
        * place
        * mobility
        * fracture
        * absence
        * replaced
        * implant
    We may add random comments
    We may add path to pics ; maybe just tell "True/False", if the path is
    obvious. Still to define
    """
    __tablename__ = 'tooth_event'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False)
    sane = Column(String, default="")
    place = Column(String, default="")
    mobility = Column(String, default="")
    fracture = Column(String, default="")
    absence = Column(String, default="")
    replaced = Column(String, default="")
    implant = Column(String, default="")


class CrownEvent(Base):
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
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False)
    side = Column(String, nullable=False)
    tooth_shade = Column(String, default="")
    # event
    sealing = Column(String, default="")
    decay = Column(String, default="")
    obturation = Column(String, default="")
    crowned = Column(String, default="")
    bridge = Column(String, default="")

class RootEvent(Base):
    """
    Root events :
    Must occur to a tooth (tooth_id)
    Are noticed while on an appointment (appointment_id)
    Occurs on root :
        * c : Central
        * v : Vestibular
        * l/p : Lingual/Palatal
        * mv : Mesio-Vestibular
        * mv2 : Mesio-Vestibular 2
        * ml/mp : Mesio-Lingual / Mesio-Palatal
        * d : Distal
        * dv : Disto-Vestibular
        * a : all
    A canal may be either :
        * sane
        * obturation
        * infected
        * apical abscess
    We may add comments
    We may use a color-code for what happened
    For the pics, see "toothevent"
    """
    __tablename__ = 'root_event'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False)
    canal = Column(String, nullable=False)
    # event
    infected = Column(String, default="")
    abscess = Column(String, default="")
    obturation = Column(String, default="")
    inlaycore = Column(String, default="")

