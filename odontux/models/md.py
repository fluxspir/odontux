# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/25
# v0.4
# Licence BSD
#


from meta import Base

from tables import (medecine_doctor_address_table, medecine_doctor_mail_table,
                    medecine_doctor_phone_table)

import sqlalchemy
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


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


