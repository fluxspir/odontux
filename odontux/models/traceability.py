# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
from tables import traceability_asset_table, traceability_kit_table
import users, assets
import sqlalchemy
import datetime

from sqlalchemy import (Table, Column, Integer, String, Numeric,
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

class SterilizationComplement(Base):
    __tablename__ = "sterilization_complement"
    id = Column(Integer, primary_key=True)
    complement = Column(String, nullable=False)

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
    user_id = Column(Integer, ForeignKey(users.OdontuxUser.id),
                                                    nullable=False)
    sterilizator_id = Column(Integer, ForeignKey(assets.Device.id),
                                                    nullable=False)
    cycle_type_id = Column(Integer, ForeignKey(SterilizationCycleType.id), 
                                                    nullable=False)
    cycle_mode_id = Column(Integer, ForeignKey(SterilizationCycleMode.id),
                                                    nullable=False)
    complement_id = Column(Integer, ForeignKey(SterilizationComplement.id),
                                                    nullable=False)
    reference = Column(String, default="")
    document = Column(String, default="")
    type = Column(String(15))

    __mapper_args__ = {
        'polymorphic_identity': 'sterilization_cycle',
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
    expiration_date = Column(Date, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'simplified_traceability'
    }

class CompleteTraceability(SterilizationCycle):
    """
        
    """
    __tablename__ = "complete_traceability"
    id = Column(Integer, ForeignKey(SterilizationCycle.id), primary_key=True)
    assets = relationship('Asset', secondary=traceability_asset_table,
                                                    backref="traceabilities")
    kits = relationship('Kit', secondary=traceability_kit_table,
                                                    backref="traceabilities")

    def number_of_items(self):
        # return func.sum(self.assets + self.kits)
        pass

    __mapper_args__ = {
        'polymorphic_identity': 'complete_traceability'
    }
