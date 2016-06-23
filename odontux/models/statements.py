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
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), 
                                                                nullable=False)
    file_id = Column(Integer, ForeignKey(documents.Files.id), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'invoice',
        'polymorphic_on': type
    }

class Quotation(Invoice):
    id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    validity = Column(Date)                         # Or make a Inverval value?
    is_accepted = Column(Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'quotation',
    }

class Bill(Invoice):
    id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    date = Column(Date, default=func.current_date(), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'bill',
    }

class QuotationGestureReference(Base):
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey(Quotation.id), nullable=False)
    gesture_id = Column(Integer, ForeignKey(acts.Gesture.id), nullable=False)
    anatomic_location = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)
    gesture = relationship('acts.Gesture')

class BillAppointmentGestureReference(Base):
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey(Bill.id), nullable=False)
    appointment_gesture_id = Column(Integer, nullable=False,
                            ForeignKey(acts.AppointmentGestureReference.id))
    gesture = relationship('acts.AppointmentGestureReference')
