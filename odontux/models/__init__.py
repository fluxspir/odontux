# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/25
# v0.4
# licence BSD
#

import meta, tables
import sqlalchemy
import ConfigParser
import os

try:
    import constants
except ImportError:
    from odontux import constants

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import ZopeTransactionExtension

from users import ( OdontuxUser, DentalOffice, Settings, 
                TimeSheet, DentistTimeSheet, AssistantTimeSheet )
from md import MedecineDoctor
from administration import Patient
from contact import ( Address, Mail, Phone )
from anamnesis import (Anamnesis, MedicalHistory, Addiction, Treatment, 
                        PastSurgery, Allergy )
from anamnesis import Survey, Question
from headneck import HeadEvent, NeckEvent
from medication import DrugPrescribed, Prescription, PrescribedDrugReference
from documents import Files, Thumbnail
from schedule import Agenda, Appointment, AppointmentMemo
from endobuccal import (MouthEvent, SuperiorLipEvent, InferiorLipEvent, 
                        LeftCheekEvent, RightCheekEvent,HardPalateEvent, 
                        SoftPalateEvent, TongueEvent, MouthBaseEvent, 
                        UvulaEvent)
from teeth import (Tooth, Event, ToothEvent, CrownEvent, RootCanalEvent,
                    Gum, PeriodontalEvent )
from act import ( Specialty, HealthCarePlan, Gesture, ClinicGesture, Cotation,
                ClinicGestureCotationReference, AppointmentCotationReference,
                ClinicReport, HealthCarePlanUserReference) 
from compta import PaymentType, Payment
from assets import (AssetProvider, AssetCategory, MaterialCategory,
                    Asset, Device, Material, AssetKitStructure, AssetKit,
                    SuperAssetCategory, SuperAsset,
                    MaterialCategoryClinicGestureReference)
from traceability import (SterilizationCycleType, SterilizationCycleMode,
                            SterilizationCycle, AssetSterilized, 
                            MaterioVigilance)
from statements import ( Invoice, Quote, Bill, QuoteGestureReference,
                            BillAppointmentCotationReference)
from certificates import Certificate

from cost import OperationalCost

if constants.LOCALE == 'br':
    from statements import NotaFiscalBr

def init():
    parser = ConfigParser.ConfigParser()
    home = os.path.expanduser("~")
    parser.read(os.path.join(home, ".odontuxrc"))
    db_url = parser.get("db", "url")

    engine = create_engine(db_url, echo=False, convert_unicode=True)
#    Session = sessionmaker(bind=engine)
    Session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
    meta.session = Session()

