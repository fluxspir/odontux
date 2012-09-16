# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/16
# v0.4
# Licence BSD
#

from meta import Base
import act
import datetime

from sqlalchemy import Table, Column, Integer, String, Boolean, Numeric
from sqlalchemy import ForeignKey

today = datetime.date.today()

payment_act_table = Table('payment_act', Base.metadata,
Column('act_id', Integer, ForeignKey('act_appointment_reference.id')),
Column('payment_id', Integer, ForeignKey('payment.id'))
)

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
    payer_id = Column(Integer, ForeignKey(administration.Patient.id), 
                        nullable=False)
    mean_id = Column(Integer, ForeignKey(PaymentType.id), nullable=False)
    amount = Column(Numeric, nullable=False)
    advance = Column(Boolean, default=False, nullable=False)
    comments = Column(String)
    cashin_date = Column(Date, default=today)
    acts_id = relationship("ActAppointmentReference",
                          secondary=payment_act_table,
                          backref="payments")

