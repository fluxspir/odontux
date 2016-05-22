# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# licence BSD
#
from meta import Base
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
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm import relationship, backref

class Survey(Base):
    """
        Could be "anamnesis adult complete", "anamnesis adult resume"
         "anamnesis before implants" ...
    """
    __tablename__ = 'survey'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    
    questions = association_proxy('SurveyQuestionsOrder', 'question',
                        creator=lambda p, q:
                            SurveyQuestionsOrder(position=p,
                                                question=q)
                        )

class Question(Base):
    """ """
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False, unique=True)

class SurveyQuestionsOrder(Base):
    """ """
    __tablename__ = 'survey_questions_order'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey(Survey.id), primary_key=True)
    question_id = Column(Integer, ForeignKey(Question.id), primary_key=True)
    position = Column(Integer, nullable=False)
    survey = relationship('Survey', backref='survey_questions',
                    collection_class=attribute_mapped_collection('position')
                    )
    question = relationship('Question')

class Anamnesis(Base):
    """ """
    __tablename__ = 'anamnesis'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    question_id = Column(Integer, ForeignKey(Question.id))
    alert = Column(Boolean, default=False)
    time_stamp = Column(Date, default=func.current_date())
    anamnesis_type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'anamnesis',
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
    __tablename__ = 'past_surgery'
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
    __tablename__ = 'allergy'
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    allergen = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    reaction = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'allergy'
    }

