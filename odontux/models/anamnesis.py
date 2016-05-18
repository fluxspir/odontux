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



class MedicalHistory(Base):
    """
        type : cf constants.ANAMNESIS
    """
    __tablename__ = 'medical_history'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    name = Column(String, nullable=False)
    icd = Column(String)
    comment = Column(String)
    alert = Column(Boolean, default=False)
    time_stamp = Column(Date, default=func.current_date())
    type = Column(Integer, nullable=False)

    
class Addiction(Base):
    """
        type : constants.ADDICTIONS
    """
    __tablename__ = 'addiction'
    id = Column(Integer, ForeignKey(Anamnesis.id), primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    type = Column(Integer, nullable=False)
    comment = Column(String)
    begin = Column(Date)
    end = Column(Date)
    alert = Column(Boolean, default=False)
    

class Treatment(Base):
    __tablename__ = "treatment"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    anamnesis_id = Column(Integer, ForeignKey(Anamnesis.id))
    name = Column(String)
    begin = Column(Date)
    end = Column(Date)
    alert = Column(Boolean, default=False)


class PastSurgeries(Base):
    __tablename__ = 'past_surgeries'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    surgery_type = Column(String, default="")
    problem = Column(String, default="")
    complication = Column(String, default="")
    time_stamp = Column(Date, default=func.current_date())
    alert = Column(Boolean, default=False)

class Allergy(Base):
    """
        type : constants.ALLERGIES
    """
    __tablename__ = 'allergies'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey(administration.Patient.id),
                                                        nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                        nullable=False)
    name = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    reaction = Column(Integer)
    alert = Column(Boolean, default=False)

