# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/17
# v0.4
# Licence BSD
#

from meta import Base

from sqlalchemy import Table, Column, Integer
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

