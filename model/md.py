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


md_address_table = Table('md_address', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)


class MedecineDoctor(Base):
    __tablename__ = 'medecine_doctor'
    id = Column(Integer, primary_key=True)
    lastname = Column(String, nullable=False)
    firstname = Column(String)
    address = relationship("Address", secondary=md_address_table,
                           backref="md")
    city = Column(String)
    address = Column(String)
    phone = Column(String)
    mail = Column(String)
    patient = relationship("Patient", backref="md")



