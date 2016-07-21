# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/23
# v0.5
# Licence BSD
#

from meta import Base
import administration, documents, users, schedule

import sqlalchemy
from sqlalchemy import ( Table, Column, Integer, String, Numeric, Boolean, 
                        DateTime )
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
try : 
    from odontux import constants
except ImportError:
    import constants

class Certificate(Base):
    __tablename__ = 'certificate'
    id = Column(Integer, primary_key=True)
    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id), 
                                                                nullable=False)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                                nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                                nullable=False)
    file_id = Column(Integer, ForeignKey(documents.Files.id), nullable=False)
    certif_type = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now())

    __mapper_args__ = {
        'polymorphic_identity': 'certificate',
        'polymorphic_on': certif_type,
    }

class Requisition(Certificate):
    __tablename__ = 'requisition'
    id = Column(Integer, ForeignKey(Certificate.id), primary_key=True)
    requisition_type = Column(Integer, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.FILE_REQUISITION
    }

class Presence(Certificate):
    __tablename__ = 'presence'
    id = Column(Integer, ForeignKey(Certificate.id), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': constants.FILE_PRESENCE
    }

class Cessation(Certificate):
    __tablename__ = 'cessation'
    id = Column(Integer, ForeignKey(Certificate.id), primary_key=True)
    days_number = Column(Numeric, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': constants.FILE_CESSATION
    }
