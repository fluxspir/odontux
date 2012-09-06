# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

# This variable gets populated by model.init(). It is shared across the entire
# application and serves as the main session.
session = None


patient_address_table = Table('patient_address', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)

md_address_table = Table('md_address', Base.metadata,
Column('md_id', Integer, ForeignKey('md.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)

user_address_table = Table('user_address', Base.metadata,
Column('user_id', Integer, ForeignKey('user.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)
