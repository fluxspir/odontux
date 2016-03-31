# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#

from meta import Base
import headneck
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import func

class SuperiorLip(Base):
    __tablename__ = 'superior_lip'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class InferiorLip(Base):
    __tablename__ = 'inferior_lip'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class LeftCheek(Base):
    __tablename__ = 'left_cheek'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class RightCheek(Base):
    __tablename__ = 'right_cheek'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class HardPalate(Base):
    __tablename__ = 'hard_palate'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class SoftPalate(Base):
    __tablename__ = 'soft_palate'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class Tongue(Base):
    __tablename__ = 'tongue'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())


class MouthBase(Base):
    __tablename__ = 'mouth_base'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String, default="")
    comments = Column(String, default="")
    time_stamp = Column(DateTime, default=func.now())

