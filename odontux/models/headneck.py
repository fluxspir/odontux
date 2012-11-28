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
    comments = Column(String, default="")
    pic = Column(String)


class Neck(Base):
    __tablename__ = 'neck'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    comments = Column(String, default="")
    pic = Column(String, default="")


class Mouth(Base):
    __tablename__ = 'mouth'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                        nullable=False)
    superiorlip = relationship("SuperiorLip", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    inferiorlip = relationship("InferiorLip", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    leftcheek = relationship("LeftCheek", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    rightcheek = relationship("RightCheek", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    hardpalate = relationship("HardPalate", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    softpalate = relationship("SoftPalate", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    tongue = relationship("Tongue", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    mouthbase = relationship("MouthBase", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
#    superioralveolarbone = relationship("SuperiorAlveolarBone", uselist=False,
#                               backref="mouth", 
#                               cascade="all, delete, delete-orphan")
#    inferioralveolarbone = relationship("InferiorAlveolarBone", uselist=False,
#                               backref="mouth", 
#                               cascade="all, delete, delete-orphan")
    superiorgum = relationship("SuperiorGum", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    inferiorgum = relationship("InferiorGum", uselist=False, backref="mouth",
                               cascade="all, delete, delete-orphan")
    teeth = relationship("Tooth", backref="mouth",
                               cascade="all, delete, delete-orphan")
