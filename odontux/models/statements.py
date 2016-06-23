# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/23
# v0.5
# Licence BSD
#

from meta import Base
import administration, acts, documents

import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, Numeric, Boolean
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy


class Invoice(Base):
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id, 
                                                                nullable=False)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id, 
                                                                nullable=False)
    file_id = Column(Integer, ForeignKey(documents.Files.id, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

class Quotation(Invoice):
    id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    validity = Column(Date)                         # Or make a Inverval value?
    is_accepted = Column(Boolean, default=False)

class Bill(Invoice):
    id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    date = Column(Date, default=func.current_date(), nullable=False)

class InvoiceGestureReference(Base):
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey(Quotation.id), nullable=False)
    gesture_id = Column(Integer, ForeignKey(acts.Gesture.id), nullable=False)
    realisation_date = Column(Date)                     # Used in case of Bill
    price = Column(Numeric, nullable=False)
