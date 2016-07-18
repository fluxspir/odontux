# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import schedule
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, DateTime
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship
import datetime


class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    md5 = Column(String(32), unique=True, nullable=False)
    file_type = Column(Integer, nullable=False)
    mimetype = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    thumbnails = relationship('Thumbnail')

class Thumbnail(Base):
    __tablename__ = 'thumbnail'
    id = Column(Integer, primary_key=True)
    md5 = Column(String(32), unique=True, nullable=False)
    size = Column(String)
    mimetype = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    file_id = Column(Integer, ForeignKey(Files.id))

