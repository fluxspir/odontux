# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/17
# v0.4
# Licence BSD
#

from meta import Base

from sqlalchemy import Table, Column, Integer, Numeric, Date, Boolean
from sqlalchemy import ForeignKey, MetaData


# act.py / compta.py
payment_act_table = Table('payment_act', Base.metadata,
Column('act_id', Integer, ForeignKey('appointment_act_reference.id')),
Column('payment_id', Integer, ForeignKey('payment.id'))
)

# administration.py
family_address_table = Table('family_address', Base.metadata,
Column('family_id', Integer, ForeignKey('family.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)

patient_mail_table = Table('patient_mail', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)

patient_phone_table = Table('patient_phone', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

family_payer_table = Table('family_payer', Base.metadata,
Column('family_id', Integer, ForeignKey('family.id')),
Column('payer_id', Integer, ForeignKey('payer.id'))
)

# administration.py / cotation.py
patient_healthcare_plan_table = Table('patient_healthcare_plan', Base.metadata,
Column('patient_id', Integer, ForeignKey('patient.id')),
Column('healthcare_plan_id', Integer, ForeignKey('healthcare_plan.id'))
)

# user.py / administration.py
odontux_user_address_table = Table('odontux_user_address', Base.metadata,
Column('odontux_user_id', Integer, ForeignKey('odontux_user.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)
odontux_user_mail_table = Table('odontux_user_mail', Base.metadata,
Column('odontux_user_id', Integer, ForeignKey('odontux_user.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
odontux_user_phone_table = Table('odontux_user_phone', Base.metadata,
Column('odontux_user_id', Integer, ForeignKey('odontux_user.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)
dental_office_address_table = Table('dental_office_address', Base.metadata,
Column('dental_office_id', Integer, ForeignKey('dental_office.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)
dental_office_mail_table = Table('dental_office_mail', Base.metadata,
Column('dental_office_id', Integer, ForeignKey('dental_office.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
dental_office_phone_table = Table('dental_office_phone', Base.metadata,
Column('dental_office_id', Integer, ForeignKey('dental_office.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

# md.py / administration.py
medecine_doctor_address_table = Table('medecine_doctor_address', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('address_id', Integer, ForeignKey('address.id'))
)
medecine_doctor_mail_table = Table('medecine_doctor_mail', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('mail_id', Integer, ForeignKey('mail.id'))
)
medecine_doctor_phone_table = Table('medecine_doctor_phone', Base.metadata,
Column('medecine_doctor_id', Integer, ForeignKey('medecine_doctor.id')),
Column('phone_id', Integer, ForeignKey('phone.id'))
)

# assets.py / administration.py
asset_provider_address_table = Table("asset_provider_address", Base.metadata,
Column("asset_provider_id", Integer, ForeignKey("asset_provider.id")),
Column("address_id", Integer, ForeignKey("address.id"))
)

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

# anamnesis.py
questionnary_question_table = Table('questionnary_question', Base.metadata,
Column('questionnary_id', Integer, ForeignKey('questionnary.id')),
Column('question_id', Integer, ForeignKey('question.id'))
)

