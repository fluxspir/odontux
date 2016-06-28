# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/23
# v0.5
# Licence BSD
#

import pdb
from meta import Base
import administration, act, documents, users, schedule

import sqlalchemy
from sqlalchemy import ( Table, Column, Integer, String, Numeric, Boolean, 
                        DateTime, Date, Interval )
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

try:
    from odontux import constants
except ImportError:
    import constants


class Invoice(Base):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id), 
                                                                nullable=False)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), 
                                                                nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    file_id = Column(Integer, ForeignKey(documents.Files.id))
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    type = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.FILE_INVOICE,
        'polymorphic_on': type
    }

class Quotation(Invoice):
    __tablename__ = 'quotation'
    id = Column(Integer, ForeignKey(Invoice.id), primary_key=True)
    validity = Column(Date)                         # Or make a Inverval value?
    treatment_duration = Column(Interval)
    is_accepted = Column(Boolean, default=False)
    
    def total_price(self):
        price = 0
        for gesture in self.gestures:
            price += gesture.price
        return price

    __mapper_args__ = {
        'polymorphic_identity': constants.FILE_QUOTATION,
    }

class Bill(Invoice):
    __tablename__ = 'bill'
    id = Column(Integer, ForeignKey(Invoice.id), primary_key=True)
    date = Column(Date, default=func.current_date(), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.FILE_BILL,
    }

class QuotationGestureReference(Base):
    __tablename__ = 'quotation_gesture_reference'
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey(Quotation.id), nullable=False)
    cotation_id = Column(Integer, ForeignKey(act.Cotation.id), nullable=False)
    gesture_id = Column(Integer, ForeignKey(act.Gesture.id), nullable=False)
    anatomic_location = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)
    appointment_number = Column(Integer, default=0)
    quotation = relationship('Quotation', backref='gestures')
    gesture = relationship('act.Gesture')

class BillAppointmentGestureReference(Base):
    __tablename__ = 'bill_appointment_gesture_reference'
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey(Bill.id), nullable=False)
    appointment_gesture_id = Column(Integer,
                            ForeignKey(act.AppointmentGestureReference.id),
                            nullable=False)
    appointment_gesture = relationship('act.AppointmentGestureReference')
