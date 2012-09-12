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


now = datetime.datetime.now()
today = datetime.date.today()


class SuperiorLip(Base):
    __tablename__ = 'superior_lip'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class InferiorLip(Base):
    __tablename__ = 'inferior_lip'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class LeftCheek(Base):
    __tablename__ = 'left_cheek'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class RightCheek(Base):
    __tablename__ = 'right_cheek'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class HardPalate(Base):
    __tablename__ = 'hard_palate'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class SoftPalate(Base):
    __tablename__ = 'soft_palate'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class Tongue(Base):
    __tablename__ = 'tongue'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)


class MouthBase(Base):
    __tablename__ = 'mouth_base'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id))
    name = Column(String)
    comments = Column(String)
    time_stamp = Column(DateTime, default=now)

