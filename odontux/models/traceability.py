# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
from tables import traceability_good_table, traceability_kit_table
import users, goods
import sqlalchemy
import datetime

from sqlalchemy import (Table, Column, Integer, String, 
                        Date, DateTime, Interval,
                        Boolean)
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref

class SterilizationCycleType(Base):
    """ Cycle can be of type : 
        * Test cycle
        * Stérilization cycle
        * Both ?
    """
    __tablename__ = "sterilization_cycle_type"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class SterilizationCycleMode(Base):
    """
        Cycles mode :
        name : easy name to choose mode
        sterilization : dry, vapor, chemical
        temperature : 
        pressure : 
        sterilization_duration : in seconds
        comment : 
    """
    __tablename__ = "sterilization_cycle_mode"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    heat_type = Column(String, nullable=False)
    temperature = Column(Numeric, nullable=False)
    pressure = Column(Numeric)
    sterilization_duration = Column(Interval, nullable=False)
    comment = Column(String)

class SterilizationCycle(Base):
    __tablename__ = "sterilization_cycle"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    operator = Column(Integer, ForeignKey(users.OdontuxUser.id),
                                                    nullable=False)
    sterilizator_id = Column(Integer, ForeignKey(goods.Equipment.id),
                                                    nullable=False)
    cycle_type_id = Column(Integer, ForeignKey(SterilizationCycleType.id), 
                                                    nullable=False)
    cycle_mode_id = Column(Integer, ForeignKey(SterilizationCycleMode.id),
                                                    nullable=False)
    date = Column(DateTime, nullable=False)
    cycle_number = Column(Integer, nullable=False, unique=True)
    reference = Column(Integer, default=0, unique=True)
    complement = Column(String, default="")
    document = Column(String, default="")

    type = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity': 'sterilization_cycle'
        'polymorphic_on': type
    }

class SimplifiedTraceability(SterilizationCycle):
    """
        Number of items in the cycle
        Number of days in seconds before peremption
    """
    __tablename__ = "simplified_traceability"
    id = Column(Integer, ForeignKey(SterilizationCycle.id), primary_key=True)
    number_of_items = Column(Integer, nullable=False)
    validity = Column(Interval, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'simplified_traceability'
    }

class CompleteTraceability(SterilizationCycle):
    """
        
    """
    __tablename__ = "complete_traceability"
    id = Column(Integer, ForeignKey(SterilizationCycle.id), primary_key=True)
    goods = relationship('Good', secondary=traceability_good_table,
                                                    backref="traceabilities")
    kits = relationship('Kit', secondary=traceability_kit_table,
                                                    backref="traceabilities")

    def number_of_items(self):
        pass

    __mapper_args__ = {
        'polymorphic_identity': 'complete_traceability'
    }
