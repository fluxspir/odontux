# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import users, administration, headneck, schedule
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey


now = datetime.datetime.now()
today = datetime.date.today()


class Tooth(Base):
    """
    A tooth has to be in a mouth ;
    A tooth has to have a name, the choice is free to name it whatever you want
    A tooth is either :
        * None : The tooth never made speak from her.
        * s : sane ; a root-infected tooth may appear sane !
        * x : sealing
        * o : obturation
        * C : crowned
        * d : decayed
        * p : place
        * m : mobility
        * f : fracture
        * a : absent
        * B : bridge
        * r : resin (prosthetic mobile)
        * I : implant
    We may put it under surveillance.
    """
    __tablename__ = 'tooth'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id), nullable=False)
    name = Column(String, nullable=False)
    state = Column(String, default=None)
    surveillance = Column(Boolean, default=False)


class ToothEvent(Base):
    """
    A tooth event is an event we can't really class neither as a crown event,
    nor as a root event.
    A tooth event has to occur to a tooth (tooth_id)
    We have to note it during an appointment (appointment_id)
    Event that can occur :
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
    tooth_id = Column(Integer, ForeignKey(Tooth.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                nullable=False)
    sane = Column(String)
    place = Column(String)
    mobility = Column(String)
    fracture = Column(String)
    absence = Column(String)
    replaced = Column(String)
    implant = Column(String)
    comments = Column(String)
    color = Column(String)
    pic = Column(String)


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
    tooth_id = Column(Integer, ForeignKey(Tooth.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                nullable=False)
    side = Column(String, nullable=False)
    sealing = Column(String)
    decay = Column(String)
    obturation = Column(String)
    crowned = Column(String)
    bridge = Column(String)
    comments = Column(String)
    color = Column(String)
    pic = Column(String)


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
        * abscess
    We may add comments
    We may use a color-code for what happened
    For the pics, see "toothevent"
    """
    __tablename__ = 'root_event'
    id = Column(Integer, primary_key=True)
    tooth_id = Column(Integer, ForeignKey(Tooth.id), nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                nullable=False)
    canal = Column(String, nullable=False)
    infected = Column(String)
    abscess = Column(String)
    obturation = Column(String)
    inlaycore = Column(String)
    comments = Column(String)
    color = Column(String)
    pic = Column(String)
