# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
from tables import questionnary_question_table
import administration, schedule
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
    """ """
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    question = Column(String)

class Anamnesis(Base):
    """ """
    __tablename__ = 'anamnesis'
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    alert = Column(Boolean, default=False)
    time_stamp = Column(Date, default=func.current_date())
    anamnesis_type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'anamnesis'
        'polymorphic_on': anamnesis_type
    }

class MedicalHistory(Anamnesis):
    """
        type : cf constants.MEDICAL_HISTORIES
    """
    __tablename__ = 'medical_history'
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    type = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    icd = Column(String)
    comment = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_history'
    }
    
class Addiction(Anamnesis):
    """
        type : constants.ADDICTIONS
    """
    __tablename__ = 'addiction'
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    type = Column(Integer, nullable=False)
    comment = Column(String)
    begin = Column(Date)
    end = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': 'addiction'
    }

class Treatment(Anamnesis):
    __tablename__ = "treatment"
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    name = Column(String)
    posologia = Column(String)
    begin = Column(Date)
    end = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': 'treatment'
    }

class PastSurgery(Anamnesis):
    __tablename__ = 'past_surgeries'
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    surgery_type = Column(String)
    problem = Column(String)
    complication = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'past_surgery'
    }

class Allergy(Anamnesis):
    """
        type : constants.ALLERGIES
    """
    __tablename__ = 'allergies'
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    reaction = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'allergy'
    }

