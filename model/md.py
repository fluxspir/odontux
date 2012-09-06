# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/25
# v0.4
# Licence BSD
#


from meta import Base
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


medecine_doctor_address_table = Table('medecine_doctor_address', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)
medecine_doctor_mail_table = Table('medecine_doctor_mail', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
medecine_doctor_phone_table = Table('medecine_doctor_phone', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

class MedecineDoctor(Base):
    __tablename__ = 'medecine_doctor'
    id = Column(Integer, primary_key=True)
    lastname = Column(String, nullable=False)
    firstname = Column(String)
    addresses = relationship("Address", secondary=\
                medecine_doctor_address_table, backref="medecine_doctor")
    phones = relationship("Phone", secondary=medecine_doctor_phone_table,
                          backref="medecine_doctor")
    mails = relationship("Mail", secondary=medecine_doctor_mail_table,
                         backref="medecine_doctor")
    patient = relationship("Patient", backref="medecine_doctor")


