# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
from tables import questionnary_question_table
import users, administration, schedule
import sqlalchemy
import datetime

try:
    import constants
except ImportError:
    from odontux import constants

from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref

class Response(Base):
    __tablename__ = 'response'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    patient = relationship('Patient')
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'response',
        'polymorphic_on': type
    }

class CloseResponse(Response):
    """ Response may be "yes", "no", or "don't know" 
        may be developped in the comment
    """
    __tablename__ = 'close_response'
    id = Column(Integer, ForeignKey(Response.id), primary_key=True)
    response = Column(Integer)
    comment = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'close'
    }

class OpenResponse(Response):
    """ Response made as a sentence """
    __tablename__ = 'open_response'
    id = Column(Integer, ForeignKey(Response.id), primary_key=True)
    response = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'open'
    }

class Questionnary(Base):
    """
        Could be "anamnesis adult complete", "anamnesis adult resume"
         "anamnesis before implants" ...
    """
    __tablename__ = 'questionnary'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    questions = relationship('Question', secondary=questionnary_question_table,
                                        backref='questionnaries')

class Question(Base):
    """
        alert_on : What we want to create an alert; could be "sim", "no", 
        "any sentence" ; the keyword of alert_on will be search on the
        Response.response 
    """
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    question = Column(String)
    open = Column(Boolean, default=False)
    alert_on = Column(String, default=None)

#class MedicalHistory(Base):
#    __tablename__ = 'medical_history'
#    id = Column(Integer, primary_key=True)
#    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
#    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
#    icd10 = Column(String, default="")
#    disease = Column(String, default="")
#    disorder = Column(String, default="")
#    habitus = Column(String, default="")
#    treatment = Column(String, default="")
#    time_stamp = Column(Date, default=func.current_date())
#
#class PastSurgeries(Base):
#    __tablename__ = 'past_surgeries'
#    id = Column(Integer, primary_key=True)
#    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
#    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
#    surgery_type = Column(String, default="")
#    problem = Column(String, default="")
#    complication = Column(String, default="")
#    time_stamp = Column(Date, default=func.current_date())
#
#class Allergies(Base):
#    __tablename__ = 'allergies'
#    id = Column(Integer, primary_key=True)
#    patient_id = Column(Integer, ForeignKey(administration.Patient.id))
#    dentist_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
#    drug = Column(String, default="")
#    metal = Column(String, default="")
#    food = Column(String, default="")
#    other = Column(String, default="")
#    reaction = Column(String, default="")
#    time_stamp = Column(Date, default=func.current_date())
