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

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, backref


locale = "fr"
socialsecuritylocale = "SocialSecurity" + locale.title()
SocialSecurityLocale = socialsecuritylocale
#SocialSecurityLocale = getattr(administration, socialsecuritylocale)


now = datetime.datetime.now()
today = datetime.date.today()


patient_address_table = Table('patient_address', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)

patient_mail_table = Table('patient_mail', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)

patient_phone_table = Table('patient_phone', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    street = Column(String)
    building = Column(String)
    city = Column(String, default="")
    postal_code = Column(String, default="")
    county = Column(String, default="")
    country = Column(String, default="France")
    update_date = Column(Date, default=today)


class Mail(Base):
    __tablename__ = 'mail'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    update_date = Column(Date, default=today)


class Phone(Base):
    __tablename__ = 'phone'
    id = Column(Integer, primary_key=True)
    phone_num = Column(String)
    update_date = Column(Date, default=today)


class SocialSecurityFr(Base):
    __tablename__ = 'social_security_fr'
    id = Column(Integer, primary_key=True)
    number = Column(String)
    patients = relationship("Patient", backref="socialsecuritynumber")
    payer = Column(Integer, ForeignKey(Patient.id))
    cmu = Column(Boolean, default=False)


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    lastname = Column(String, nullable=False)
    firstname = Column(String)
    qualifications = Column(String)
    preferred_name = Column(String)
    correspondence_name = Column(String)
    addresses = relationship("Address", secondary=patient_address_table,
                           backref="patient")
    sex = Column(Boolean)
    dob = Column(Date, default="19700101")                  # date of birth
    job = Column(String)
    phones = relationship("Phone", secondary=patient_phone_table,
                         backref="patient")
    mails = relationship("Mail", secondary=patient_mail_table,
                        backref="patient")
    inactive = Column(Boolean, default=False)
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id), default=2)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), default=1)
    gen_doc_id = Column(Integer, ForeignKey(md.MedecineDoctor.id))
    time_stamp = Column(Date, default=today)
    head = relationship("Head", uselist=False, backref="patient", 
                        cascade="all, delete, delete-orphan")
    neck = relationship("Neck", uselist=False, backref="patient",
                        cascade="all, delete, delete-orphan")
    mouth = relationship("Mouth", uselist=False, backref="patient", 
                        cascade="all, delete, delete-orphan")
    appointments = relationship("Appointment", backref="patient",
                        cascade="all, delete, delete-orphan")
    socialsecuritynumber_id = Column(Integer, 
                              ForeignKey(SocialSecurityLocale.id))

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

