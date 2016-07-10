# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import users, md, contact
import sqlalchemy
import datetime

from tables import (patient_mail_table, patient_phone_table,
                    patient_healthcare_plan_table)
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    identity_number_1 = Column(String)
    identity_number_2 = Column(String)
    title = Column(String, default="Mr")
    lastname = Column(String, nullable=False)
    firstname = Column(String, default="")
    qualifications = Column(String, default="")
    preferred_name = Column(String, default="")
    correspondence_name = Column(String, default="")
    sex = Column(String, default="f")
    dob = Column(Date, default=datetime.date(1970, 1, 1))  #date of birth
    job = Column(String, default="")
    address_id = Column(Integer, ForeignKey(contact.Address.id))
    address = relationship('Address', backref='patient')
    phones = relationship("Phone", secondary=patient_phone_table,
                          backref="patient")
    mails = relationship("Mail", secondary=patient_mail_table,
                         backref="patient")
    inactive = Column(Boolean, default=False)
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
    gen_doc_id = Column(Integer, ForeignKey(md.MedecineDoctor.id))
    time_stamp = Column(Date, default=func.current_date())
    creation_date = Column(Date, default=func.current_date())
    appointments = relationship("Appointment", backref="patient",
                        cascade="all, delete, delete-orphan")
    hcs = relationship("HealthCarePlan", 
                        secondary=patient_healthcare_plan_table,
                        backref="patients",
                        cascade="all, delete")
    healthcare_plans_id = association_proxy('hcs', 'id')
    healthcare_plans = association_proxy('hcs', 'name')
    teeth = relationship("Tooth")
    teeth_codenames = association_proxy('teeth', 'codename')

    def age(self):
        return (
            datetime.date.today().year - self.dob.year
                - int((datetime.date.today().month, datetime.date.today().day) 
                < (self.dob.month, self.dob.day))
        )

    def is_birthday(self):
        if (datetime.date.today().month == self.dob.month and 
            datetime.date.today().day == self.dob.day):
            return True
        else:
            return False

    def global_price(self):
        total_price = 0
        for appointment in self.appointments:
            for gesture in appointment.administrative_gestures:
                total_price += gesture.price
        return total_price

    def already_paid(self):
        total_paid = 0
        for payment in self.payments:
            total_paid += payment.amount
        return total_paid

    def gestures_marked_as_paid(self):
        gestures_paid = 0
        for appointment in self.appointments:
            for gesture in appointment.administrative_gestures:
                if gesture.is_paid:
                    gestures_paid += gesture.price
        return gestures_paid

    def balance(self):
        return self.already_paid() - self.global_price()
