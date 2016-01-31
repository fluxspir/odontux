# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
import sqlalchemy
import datetime

now = datetime.datetime.now()

from sqlalchemy import (Table, Column, Integer, String, Date, DateTime, 
                        Boolean, Interval)
from sqlalchemy import ForeignKey


"""
A "Good" is an entity.
A "Good" may be an "Equipment", an "Instrument", or some "Material/consumible".
An "Equipment" is a machine or something fix, that can't be move or replace 
easily.
An Instrument is a tool that is currently use, generaly many times with a
process of decontamination/sterilization between uses.
A Material is a special entity that is divisible. 

"Good" has "GoodGeneral" datas that remains the same. For example, the "brand 
name", the "commercial name", the "barcode" of the product will stay the same 
between every good we buy.
Good has variable datas, for exemple the day we bought this special "Good", the
"price" we paid that special day for it...

"Material" is a type of good that owns general data. We use for that data a 
subclass of "GoodGeneral" : the "MaterialGeneral".

"Kit" is a groupment of, generally, "Instrument". But a "Kit" may contain any 
type of good.

"""

class MaterialProvider(Base):
    __tablename__ = "material_provider"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    addresses = relationship("Address", secondary=provider_address_table,
                            backref="provider")
    phones = relationship("Phone", secondary=provider_phone_table,
                            backref="provider")
    mails = relationship("Mail", secondary=provider_mail_table,
                            backref="provider")

class GoodGeneral(Base):
    """ 
        * odontux_code : pourrait = id ; ou être plus explicite ; à voir.
        * brand : The manufacturer of the product
        * commercial name of the product
        * description... indispensable ?
        * barcode : pour scanner les produits entrant en stock.
        * material_type : Famille du bien ; permet des recherches plus ciblées
                    
    """
    __tablename_ = "good_data"
    id = Column(Integer, primary_key=True)
    odontux_code = Column(String, nullable=False, unique=True) # ForeignKey=GoodName.id ???
    brand = Column(String, default="")
    commercial_name = Column(String, default="")
    description = Column(String, default="")
    barcode = Column(String, default="")

    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'good_general'
        'polymorphic_on' : type
    }

class MaterialGeneral(GoodGeneral):
    """
        General's data about Goods whose "type" is Material.

        * material_type : utilisation's family to find the material more easily
        * unity of the quantity : 
                    0 = pieces
                    1 = volume
                    2 = weight
        * initial_quantity : how much of the product there is in one box
        * automatic_decresase : quantity of unity to decrease on a specific 
            utilisation.
        * order_threshold : -1 / negative value : never order
            Other value : Items *in activity* enter in the calcul.

    """
    id = Column(Integer, ForeignKey(GoodGeneral.id), primary_key=True)
    material_type = Column(String, default="")
    order_threshold = Column(Numeric, default=-1)
    unity = Column(Integer, default=0)
    initial_quantity = Column(Numeric, default=1)
    automatic_decrease = Column(Integer, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'material_general'
    }

class Good(Base):
    """
        * material_provider_id : from whom it was bought
        * acquisition_date
        * acquisiton_price
        * product_new : true if the product is new
        * user : which user is using this good
        * office : to which dental office is related the good.
    """
    __tablename__ = "good"
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey(Provider.id), nullable=False)
    good_general_id = Column(Integer, ForeignKey(GoodName.id), nullable=False)
    good_general = relationship('GoodGeneral')
    acquisition_date = Column(DateTime, default=now)
    acquisiton_price = Column(Numeric, default=0)
    serial_number = Column(String, default="")
    new = Column(Boolean, default=True)
    user = Column(Integer, ForeignKey(users.OdontuxUser.id))
    office = Column(Integer, ForeignKey(users.DentalOffice.id))
    type = Column(String(20))
    sterilizations = relationship("")


    __mapper_args__ = {
        'polymorphic_identity': 'good',
        'polymorphic_on': type
    }

class Equipment(Good):
    __tablename__ = "equipment"
    id = Column(Integer, ForeignKey(Good.id), primary_key=True)
    lifetime_expected = Column(Interval, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'equipment',
    }

class Instrument(Good):
    """
        * lifetime expected ; 0 if forever
        * expiration_date
    """
    __tablename__ = "tool"
    id = Column(Integer, ForeignKey(Good.id), primary_key=True)


    __mapper_args__ = {
        'polymorphic_identity': 'instrument',
    }

class Material(Good):
    """
        expiration_alert : default to two weeks
        end_use_reason : 
            0 : Natural end of the material
            1 : Unconvenient
            2 : Obsolete/Out of date (périmé)
            3 : Removed from market
            4 : Lost
    """
    __tablename__ = "material"
    id = Column(Integer, ForeignKey(Good.id), primary_key=True)
    used_in_traceability_of = Column(String)
    actual_quantity = Column(Numeric, default=1)
    expiration_date = Column(Date)
    expiration_alert = Column(Interval, default=1209600)
    start_of_use = Column(Date, default=None)
    end_of_use = Column(Date, default=None)
    end_use_reason = Column(Integer, default=0)
    appointments = relationship("Appointment", 
                                secondary=material_appointment_table,
                                backref='material')

    __mapper_args__ = {
        'polymorphic_identity': 'material',
    }


class KitType(Base):
    """
    """
    __tablename__ = "kit_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)


class Kit(Base):
    """
    """
    __tablename__ = "kit"
    id = Column(Integer, primary_key=True)
    kit_type_id = Column(Integer, ForeignKey(KitType.id), nullable=False)
    goods = relationship("Good", secondary=good_kit_table,
                                        backref="kits")
    creation_date = Column(Date, nullable=False)
