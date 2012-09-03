# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
import cotation, schedule, headneck, teeth
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Numeric
from sqlalchemy import ForeignKey


locale = "fr"
cotationlocale = "Cotation" + locale.title()
CotationLocale = getattr(cotation, cotationlocale)


class Specialty(Base):
    __tablename__ = 'specialty'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ActType(Base):
    __tablename__ = 'act_type'
    id = Column(Integer, primary_key=True)
    specialty_id = Column(Integer, ForeignKey(Specialty.id))
    cotationfr_id = Column(Integer, ForeignKey(CotationLocale.id))
    name = Column(String, nullable=False)
    alias = Column(String)
    color = Column(String, default="#000000")


class AppointmentActReference(Base):
    __tablename__ = 'appointment_act_reference'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                            nullable=False)
    act_id = Column(Integer, ForeignKey(ActType.id), nullable=False)
    tooth_id = Column(Integer, ForeignKey(teeth.Tooth.id))
    code = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)

