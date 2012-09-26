# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
import headneck
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey


class SuperiorGum(Base):
    __tablename__ = 'superior_gum'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id), nullable=False)


class InferiorGum(Base):
    __tablename__ = 'inferior_gum'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id), nullable=False)


class SuperiorAlveolarBone(Base):
    __tablename__ = 'superior_alveolar_bone'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id), nullable=False)


class InferiorAlveolarBone(Base):
    __tablename__ = 'inferior_alveolar_bone'
    id = Column(Integer, primary_key=True)
    mouth_id = Column(Integer, ForeignKey(headneck.Mouth.id), nullable=False)

