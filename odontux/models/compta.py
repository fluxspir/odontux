# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/16
# v0.4
# Licence BSD
#

from meta import Base
import act, administration, documents

from sqlalchemy import (Table, Column, Integer, String, Boolean, Numeric, Date)
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref



class PaymentType(Base):
    """
    List of payment's type that may be done :
    Cash, Bank cheque, cheque, Credit_card, paypal...
    alias, for exemple : cash → $
                         cheque → chq
                         ...
    """
    __tablename__ = 'payment_type'
    id = Column(Integer, primary_key=True)
    odontux_name = Column(String, default="", nullable=False)
    gnucash_name = Column(String, default="", nullable=False)
    active = Column(Boolean, default=True)

class Majoration(Base):
    """ """
    __tablename__ = 'majoration'
    id = Column(Integer, primary_key=True)
    reason = Column(String, nullable=False, unique=True)
    percentage = Column(Numeric, nullable=False)

class Payment(Base):
    """
    mean_id = type of payment (cheque, cash...)
    comments =  
        * email address for paypal
        * banque name for bank ....
        * Whatever you want to precise
    """
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                                nullable=False)
    mean_id = Column(Integer, ForeignKey(PaymentType.id), nullable=False)
    receipt_id = Column(Integer, ForeignKey(documents.Files.id), nullable=False)
    amount = Column(Numeric, nullable=False)
    comments = Column(String, default="")
    cashin_date = Column(Date, default=func.current_date())
    mean = relationship('PaymentType', backref='payments')
    receipt = relationship('documents.Files', backref='payment')
    patient = relationship('administration.Patient', backref='payments')
