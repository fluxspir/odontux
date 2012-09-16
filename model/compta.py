# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/16
# v0.4
# Licence BSD
#

from meta import Base
import act

from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy import ForeignKey

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
    name = Column(String)
    alias = Column(String)


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
    amount = Column(Numeric, nullable=False)
    mean_id = Column(Integer, ForeignKey(PaymentType.id), nullable=False)
    advance = Column(Boolean, default=False, nullable=False)
    comments = Column(String)

class PaymentActReference(Base):
    """ 
    Table that tells exactly which act was paid.
    """
    __tablename__ = 'payment_act_reference'
    id = Column(Integer, primary_key=True)
    act_id = Column(Integer, ForeignKey(act.AppointmentActReference.id),
                    nullable=False, unique=True)
    payment_id = Column(Integer, ForeignKey(Payment.id))
