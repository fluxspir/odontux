# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, DateTime
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import relationship, func
import datetime

class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    md5 = Column(String(32), unique=True, nullable=False)
    file_type = Column(Integer, nullable=False)
    mimetype = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())

class FileAppointmentReference(Base):
    __tablename__ = 'file_appointment_reference'
    id = Column(Integer, primary_key=True
    file_id = Column(Integer, ForeignKey(Files.id), nullable=False)
    appointment_id = Colmun(Integer, ForeingKey(schedule.Appointment.id))
    file = relationship('Files')
