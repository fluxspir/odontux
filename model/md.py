# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


now = datetime.datetime.now()
today = datetime.date.today()


class GeneralistDoctor(Base):

    __tablename__ = 'generalist_doctor'

    id = Column(Integer, primary_key=True)
    lastname = Column(String, nullable=False)
    firstname = Column(String)
    city = Column(String)
    address = Column(String)
    phone = Column(String)
    mail = Column(String)
#    patients = relationship("administration.Patient")

