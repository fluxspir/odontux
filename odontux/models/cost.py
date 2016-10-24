# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/10/13
# 
# Licence BSD
#

from meta import Base
import sqlalchemy
from sqlalchemy import ( Table, Column, Integer, String, Numeric, Boolean, 
                            Interval )
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

import datetime

class OperationalCost(Base):
    __tablename__ = 'operational_cost'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    cost = Column(Numeric, nullable = False)
    periodicity = Column(Interval, nullable=False)
    active = Column(Boolean, default=True)

    def hourly(self):
        return cost / periodicity.totals_seconds() * 3600
