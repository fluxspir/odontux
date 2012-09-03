# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#
from meta import Base
import administration
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


now = datetime.datetime.now()
today = datetime.date.today()


class Head(Base):
    __tablename__ = 'head'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    comments = Column(String)
    pic = Column(String)


class Neck(Base):
    __tablename__ = 'neck'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    comments = Column(String)
    pic = Column(String)


class Mouth(Base):
    __tablename__ = 'mouth'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    superiorlip = relationship("SuperiorLip", uselist=False, backref="mouth")
    inferiorlip = relationship("InferiorLip", uselist=False, backref="mouth")
    leftcheek = relationship("LeftCheek", uselist=False, backref="mouth")
    rightcheek = relationship("RightCheek", uselist=False, backref="mouth")
    hardpalate = relationship("HardPalate", uselist=False, backref="mouth")
    softpalate = relationship("SoftPalate", uselist=False, backref="mouth")
    tongue = relationship("Tongue", uselist=False, backref="mouth")
    mouthbase = relationship("MouthBase", uselist=False, backref="mouth")
    superiorgum = relationship("SuperiorGum", uselist=False, backref="mouth")
    inferiorgum = relationship("InferiorGum", uselist=False, backref="mouth")
    teeth = relationship("Tooth", backref="mouth")
    time_stamp = Column(DateTime, default=now)
