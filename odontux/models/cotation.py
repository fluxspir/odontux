# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from meta import Base
#import meta
import act
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Numeric
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref

class PlanName(Base):
    __tablename__ = "plan_name"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
#    acts = relationship("act.ActType", backref="plan_names")

#class Cotation(Base):
#    __tablename__ = "cotation"
#    id = Column(Integer, primary_key=True)
#    plan_name_id = Column(Integer, ForeignKey(PlanName.id))
#    plan_name = relationship("PlanName", backref="cotations")
#    act_type_id = Column(Integer, ForeignKey(act.ActType.id))
#    act_type = relationship("act.ActType", backref="cotations")
##    code = Column(String, nullable=False)
#    price = Column(Numeric, default=0)
#
