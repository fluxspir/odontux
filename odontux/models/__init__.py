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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import ZopeTransactionExtension

from users import OdontuxUser, DentalOffice
from md import MedecineDoctor
from administration import (Address, Mail, Phone, SocialSecurityFr, Payer, 
                            Family, Patient)
from anamnesis import MedicalHistory, PastSurgeries, Allergies
from headneck import Head, Neck, Mouth
from medication import DrugPrescribed, Prescription, PrescribedDrugReference
from schedule import Agenda, Appointment, AppointmentMemo
from softtissues import (SuperiorLip, InferiorLip, LeftCheek, RightCheek,
                         HardPalate, SoftPalate, Tongue, MouthBase)
from periodonte import (SuperiorGum, InferiorGum, SuperiorAlveolarBone,
                        InferiorAlveolarBone)
from teeth import Tooth, Event, ToothEvent, CrownEvent, RootEvent
from act import Specialty, ActType, AppointmentActReference
from cotation import NgapKeyFr, CmuKeyFr, MajorationFr, CotationFr
from compta import PaymentType, Payment
from assets import (AssetProvider, AssetCategory, MaterialCategory,
                    Asset, Device, Material, AssetKitStructure, AssetKit)
from traceability import (SterilizationCycleType, SterilizationCycleMode,
                            SterilizationCycle, AssetSterilized)

def init():
    parser = ConfigParser.ConfigParser()
    home = os.path.expanduser("~")
    parser.read(os.path.join(home, ".odontuxrc"))
    db_url = parser.get("dbtest", "url")

    engine = create_engine(db_url, echo=False, convert_unicode=True)
#    Session = sessionmaker(bind=engine)
    Session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
    meta.session = Session()

