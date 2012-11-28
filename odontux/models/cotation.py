# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from meta import Base
import meta
import sqlalchemy
import datetime

from sqlalchemy import Table, Column, Integer, String, Numeric
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


class NgapKeyFr(Base):
    __tablename__ = 'ngap_key_fr'
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    key = Column(String, nullable=False)
    unit_price = Column(Numeric, nullable=False)

    def get_price(self, multiplicator):
        return multiplicator * self.unit_price


class CmuKeyFr(Base):
    __tablename__ = 'cmu_key_fr'
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    key = Column(String, nullable=False)


class MajorationFr(Base):
    __tablename__ = 'majoration_fr'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)


class CotationFr(Base):
    __tablename__ = 'cotation_fr'
    id = Column(Integer, primary_key=True)
    acts = relationship("ActType", backref="cotation")
    key_id = Column(Integer, ForeignKey(NgapKeyFr.id), nullable=False)
    key_cmu_id = Column(Integer, ForeignKey(CmuKeyFr.id), default=None)
    adult_multiplicator = Column(Integer, default=0)
    kid_multiplicator = Column(Integer, default=0)
    adult_cmu_num = Column(Integer, default=0)
    kid_cmu_num =Column(Integer, default=0)
    exceeding_adult_normal = Column(Numeric, default=0)
    exceeding_kid_normal = Column(Numeric, default=0)
    exceeding_adult_cmu = Column(Numeric, default=0)
    exceeding_kid_cmu = Column(Numeric, default=0)

    def get_price(self, multiplicator, exceeding=0, majoration=0):
        ngap = (
            meta.session.query(NgapKeyFr)
                   .filter(NgapKeyFr.id == self.key_id)
        ).one()

        return ngap.get_price(multiplicator) + exceeding + majoration

    def security_social(self, price):
        return price * 0.7

    def reste_a_charge(self, price):
        return price * 0.3

