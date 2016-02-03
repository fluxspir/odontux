# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
from tables import (asset_provider_address_table, asset_provider_phone_table, 
                    asset_provider_mail_table, kit_asset_table)
import users
import sqlalchemy
import datetime

from sqlalchemy import (Table, Column, Integer, String, Date, DateTime, 
                        Numeric, Boolean, Interval)
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import backref, relationship

"""
An "Asset" is an entity/item...
An "Asset" may be a "Device" or some "Material/consumible".
A "Device" is an appliance or something fix, that can't be move or replace 
easily or an instrument that is currently use, generaly many times with a
process of decontamination/sterilization between uses.
A Material is a special entity that is divisible. 

"Asset" has "AssetCategory" datas that remains the same. For example, 
the "brand name", the "commercial name", the "barcode" of the product will stay
the same between every asset we buy.
Asset has variable datas, for exemple the day we bought this special "Asset",
the "price" we paid that special day for it...

"Material" is a type of asset that owns general data. We use for that data a 
subclass of "AssetCategory" : the "MaterialCategory".

"Kit" is a groupment of, generally, "Device". But a "Kit" may contain any 
type of Asset.

"""

class AssetProvider(Base):
    __tablename__ = "asset_provider"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    addresses = relationship("Address", secondary=asset_provider_address_table,
                            backref="provider")
    phones = relationship("Phone", secondary=asset_provider_phone_table,
                            backref="provider")
    mails = relationship("Mail", secondary=asset_provider_mail_table,
                            backref="provider")

class AssetCategory(Base):
    """ 
        * odontux_code : pourrait = id ; ou être plus explicite ; à voir.
        * brand : The manufacturer of the product
        * commercial name of the product
        * description... indispensable ?
        * barcode : pour scanner les produits entrant en stock.
        * material_type : Famille du bien ; permet des recherches plus ciblées
                    
    """
    __tablename__ = "asset_category"
    id = Column(Integer, primary_key=True)
    odontux_code = Column(String, nullable=False, unique=True)
    brand = Column(String, default="")
    commercial_name = Column(String, default="")
    description = Column(String, default="")
    barcode = Column(String, default="")

    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'asset_category',
        'polymorphic_on': type
    }

class MaterialCategory(AssetCategory):
    """
        Generals' datas about Asset whose "type" is Material.

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
    __tablename__ = "material_category"
    id = Column(Integer, ForeignKey(AssetCategory.id), primary_key=True)
    material_type = Column(String, default="")
    order_threshold = Column(Numeric, default=-1)
    unity = Column(Integer, default=0)
    initial_quantity = Column(Numeric, default=1)
    automatic_decrease = Column(Integer, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'material_category'
    }

class Asset(Base):
    """
        * provider_id : from whom it was bought
        * acquisition_date
        * acquisiton_price
        * product_new : true if the product is new
        * user : which user is using this asset 
        * office : to which dental office is related the asset
    """
    __tablename__ = "asset"
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey(AssetProvider.id), nullable=False)
    asset_category_id = Column(Integer, ForeignKey(AssetCategory.id), 
                                                                nullable=False)
    asset_category = relationship('AssetCategory')
    acquisition_date = Column(DateTime, default=func.now())
    acquisiton_price = Column(Numeric, default=0)
    serial_number = Column(String, default="")
    new = Column(Boolean, default=True)
    user = Column(Integer, ForeignKey(users.OdontuxUser.id))
    office = Column(Integer, ForeignKey(users.DentalOffice.id))
    type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': type
    }

class Device(Asset):
    """
        * lifetime expected ; 0 if forever
    """
    __tablename__ = "device"
    id = Column(Integer, ForeignKey(Asset.id), primary_key=True)
    lifetime_expected = Column(Interval, default=0)

    __mapper_args__ = {
        'polymorphic_identity': 'device',
    }

class Material(Asset):
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
    id = Column(Integer, ForeignKey(Asset.id), primary_key=True)
    used_in_traceability_of = Column(String)
    actual_quantity = Column(Numeric, default=1)
    expiration_date = Column(Date)
    expiration_alert = Column(Interval, default=1209600)
    start_of_use = Column(Date, default=None)
    end_of_use = Column(Date, default=None)
    end_use_reason = Column(Integer, default=0)

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
    assets = relationship("Asset", secondary=kit_asset_table,
                                        backref="kits")
    creation_date = Column(Date, nullable=False)
