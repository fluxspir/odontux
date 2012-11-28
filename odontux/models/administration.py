# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from meta import Base
import users, md
import sqlalchemy
import datetime

from tables import (family_address_table, patient_mail_table, 
                    patient_phone_table, family_payer_table)
                    

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


locale = "fr"
#SocialSecurityLocale = getattr(administration, socialsecuritylocale)

now = datetime.datetime.now()
today = datetime.date.today()



class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    street = Column(String, default="")
    building = Column(String, default="")
    city = Column(String, default="")
    postal_code = Column(String, default="")
    county = Column(String, default="")
    country = Column(String, default="France")
    update_date = Column(Date, default=today)


class Mail(Base):
    __tablename__ = 'mail'
    id = Column(Integer, primary_key=True)
    email = Column(String, default="")
    update_date = Column(Date, default=today)


class Phone(Base):
    __tablename__ = 'phone'
    id = Column(Integer, primary_key=True)
    name = Column(String, default="")
    number = Column(String, default="")
    update_date = Column(Date, default=today)


class SocialSecurityFr(Base):
    __tablename__ = 'social_security_fr'
    id = Column(Integer, primary_key=True)
    number = Column(String, default="")
    beneficiaries = relationship("Patient", backref="socialsecurity")
    cmu = Column(Boolean, default=False)
    insurance = Column(String, default="")


class Family(Base):
    __tablename__ = 'family'
    id = Column(Integer, primary_key=True)
    members = relationship("Patient", backref="family")
    addresses = relationship("Address", secondary=family_address_table,
                             backref="family")
    payers = relationship("Payer", secondary=family_payer_table,
                           backref="family")

socialsecuritylocale = "SocialSecurity" + locale.title()
SocialSecurityLocale = locals()[socialsecuritylocale]

class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey(Family.id))
    socialsecurity_id = Column(Integer, ForeignKey(SocialSecurityLocale.id))
    title = Column(String, default="Mr")
    lastname = Column(String, nullable=False)
    firstname = Column(String, default="")
    qualifications = Column(String, default="")
    preferred_name = Column(String, default="")
    correspondence_name = Column(String, default="")
    sex = Column(String, default="f")
    dob = Column(Date, default="19700101")                  # date of birth
    job = Column(String, default="")
    phones = relationship("Phone", secondary=patient_phone_table,
                          backref="patient")
    mails = relationship("Mail", secondary=patient_mail_table,
                         backref="patient")
    inactive = Column(Boolean, default=False)
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id))
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
    gen_doc_id = Column(Integer, ForeignKey(md.MedecineDoctor.id))
    time_stamp = Column(Date, default=today)
    creation_date = Column(Date, default=today)
    head = relationship("Head", uselist=False, backref="patient", 
                        cascade="all, delete, delete-orphan")
    neck = relationship("Neck", uselist=False, backref="patient",
                        cascade="all, delete, delete-orphan")
    mouth = relationship("Mouth", uselist=False, backref="patient", 
                        cascade="all, delete, delete-orphan")
    appointments = relationship("Appointment", backref="patient",
                        cascade="all, delete, delete-orphan")

    def age(self):
        return (
            today.year - self.dob.year
             - int((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def is_birthday(self):
        if today.month == self.dob.month and today.day == self.dob.day:
            return True
        else:
            return False


class Payer(Base):
    __tablename__ = 'payer'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(Patient.id))


