# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/17
# v0.4
# Licence BSD
#

from meta import Base

from sqlalchemy import Table, Column, Integer, Numeric, Date, Boolean
from sqlalchemy import ForeignKey, MetaData


# administration.py / contact.py
patient_mail_table = Table('patient_mail', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)

patient_phone_table = Table('patient_phone', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

# administration.py / cotation.py
patient_healthcare_plan_table = Table('patient_healthcare_plan', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('healthcare_plan_id', Integer, ForeignKey('healthcare_plan.id'))
)

# user.py / contact.py
odontux_user_mail_table = Table('odontux_user_mail', Base.metadata,
Column('odontux_user_id', Integer, ForeignKey('odontux_user.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
odontux_user_phone_table = Table('odontux_user_phone', Base.metadata,
Column('odontux_user_id', Integer, ForeignKey('odontux_user.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)
dental_office_mail_table = Table('dental_office_mail', Base.metadata,
Column('dental_office_id', Integer, ForeignKey('dental_office.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
dental_office_phone_table = Table('dental_office_phone', Base.metadata,
Column('dental_office_id', Integer, ForeignKey('dental_office.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

# md.py / contact.py
medecine_doctor_mail_table = Table('medecine_doctor_mail', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
medecine_doctor_phone_table = Table('medecine_doctor_phone', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

# assets.py / contact.py
asset_provider_phone_table = Table("asset_provider_phone", Base.metadata,
Column("asset_provider_id", Integer, ForeignKey("asset_provider.id")),
Column("phone_id", Integer, ForeignKey("phone.id"))
)

asset_provider_mail_table = Table("asset_provider_mail", Base.metadata,
Column("asset_provider_id", Integer, ForeignKey("asset_provider.id")),
Column("mail_id", Integer, ForeignKey("mail.id"))
)

# assets.py
superassetcategory_assetcategory_table = Table(
                    'superassetcategory_assetcategory_table', Base.metadata,
Column("superassetcategory_id", Integer, 
                                ForeignKey("super_asset_category.id")),
Column("assetcategory_id", Integer, ForeignKey("asset_category.id"))
)

superasset_asset_table = Table("superasset_asset", Base.metadata,
Column("superasset_id", Integer, ForeignKey("super_asset.id")),
Column("asset_id", Integer, ForeignKey("asset.id"))
)

kit_asset_table = Table("kit_asset", Base.metadata,
Column("kit_id", Integer, ForeignKey("asset_kit.id")),
Column("asset_id", Integer, ForeignKey("asset.id"))
)

kitstructure_assetcategory_table = Table("kit_structure_asset_category", 
                                                                Base.metadata,
Column("kit_structure_id", Integer, ForeignKey("asset_kit_structure.id")),
Column("asset_category_id", Integer, ForeignKey("asset_category.id"))
)

kitstructure_superassetcategory_table = Table("kit_structure_superasset_category",
                                                            Base.metadata,
Column("kit_structure_id", Integer, ForeignKey("asset_kit_structure.id")),
Column("superasset_category_id", Integer, ForeignKey("super_asset_category.id"))
)

# assets - act
material_category_gesture_table = Table('material_category_gesture', 
                                                            Base.metadata,
Column("material_category_id", Integer, ForeignKey('material_category.id')),
Column("gesture_id", Integer, ForeignKey('gesture.id'))
)

# act - traceability
clinic_report_materio_vigilance_table = Table('clinic_report_materio_vigilance', 
                                                                Base.metadata,
Column("clinic_report_id", Integer, ForeignKey('clinic_report.id')),
Column("materio_vigilance_id", Integer, ForeignKey('materio_vigilance.id'))
)

# teeth.py / documents.py
teeth_event_file_table = Table("teeth_event_file", Base.metadata,
Column("teeth_event_id", Integer, ForeignKey("event.id")),
Column("file_id", Integer, ForeignKey("files.id"))
)
