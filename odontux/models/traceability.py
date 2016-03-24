# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
#from tables import traceability_asset_table, traceability_kit_table
import users, assets, schedule
import sqlalchemy
import datetime

from sqlalchemy import (Table, Column, Integer, String, Numeric,
                        Date, DateTime, Interval,
                        Boolean)
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref

class SterilizationCycleType(Base):
    """ Cycle Name can be of type : 
        * Test cycle
        * Stérilization cycle
        * Both ?
    """
    __tablename__ = "sterilization_cycle_type"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class SterilizationComplement(Base):
    """
        the complement is, for exemple, the prion's cycle indicator that was
        conform or not.
        Any other complement may be add.
    """
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
    """
        reference = cycle's internal number of the autoclave, or any other
            reference we'd like.
        document = path to scanned document or anything else.
    """
    __tablename__ = "sterilization_cycle"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey(users.OdontuxUser.id),
                                                    nullable=False)
    user = relationship("users.OdontuxUser")
    sterilizer_id = Column(Integer, ForeignKey(assets.Device.id),
                                                    nullable=False)
    sterilizer = relationship("assets.Device")
    cycle_type_id = Column(Integer, ForeignKey(SterilizationCycleType.id), 
                                                    nullable=False)
    cycle_type = relationship("SterilizationCycleType")
    cycle_mode_id = Column(Integer, ForeignKey(SterilizationCycleMode.id),
                                                   nullable=False)
    cycle_mode = relationship("SterilizationCycleMode")
    cycle_complement_id = Column(Integer, ForeignKey(
                                SterilizationComplement.id), nullable=False)
    cycle_complement = relationship("SterilizationComplement")
    cycle_date = Column(Date, nullable=False)
    reference = Column(String, default="")
    document = Column(String, default="")

class AssetSterilized(Base):
    """ """
    __tablename__ = "asset_sterilized"
    id = Column(Integer, primary_key=True)
    sterilization_cycle_id = Column(Integer, ForeignKey(SterilizationCycle.id),
                                                                nullable=False)
    asset_id = Column(Integer, ForeignKey(assets.Asset.id), default=None)
    kit_id = Column(Integer, ForeignKey(assets.AssetKit.id), default=None)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id), 
                                                                default=None)
    expiration_date = Column(Date, nullable=False)

