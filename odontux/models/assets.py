# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from meta import Base
import meta
from tables import (asset_provider_address_table, asset_provider_phone_table, 
                    asset_provider_mail_table, kit_asset_table,
                    kitstructure_assetcategory_table)
import users, act, schedule
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

#class BarcodeType(Base):
#    __tablename__ = "barcode_type"
#    id = Column(Integer, primary_key=True)
#    dimension = Column(Integer(1), nullable=False)
#    name = Column(String(15), nullable=False)
#

class AssetProvider(Base):
    """ 
        status : if True, we work we
    """
    __tablename__ = "asset_provider"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)
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
        * asset_type : Famille du bien ; permet des recherches plus ciblées
                    
    """
    __tablename__ = "asset_category"
    id = Column(Integer, primary_key=True)
    barcode = Column(String, unique=True, nullable=True)
    brand = Column(String, default="", nullable=False)
    commercial_name = Column(String, default="", nullable=False)
    description = Column(String, default="")
    asset_specialty_id = Column(Integer, ForeignKey(act.Specialty.id))
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': type
    }

class DeviceCategory(AssetCategory):
    __tablename__ = "device_category"
    id = Column(Integer, ForeignKey(AssetCategory.id), primary_key=True)
    sterilizable = Column(Boolean, nullable=False)
    validity = Column(Interval, default=datetime.timedelta(15))
    sterilizer = Column(Boolean, default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'device'
    }

class MaterialCategory(AssetCategory):
    """
        Generals' datas about Asset whose "type" is Material.

        * unity of the quantity : 
                    0 = pieces
                    1 = volume
                    2 = weight
                    3 = length
        * initial_quantity : how much of the product there is in one box
        * automatic_decresase : quantity of unity to decrease on a specific 
            utilisation.
        * order_threshold : -1 / negative value : never order
            Other value : Items *in activity* enter in the calcul.

    """
    __tablename__ = "material_category"
    id = Column(Integer, ForeignKey(AssetCategory.id), primary_key=True)
    order_threshold = Column(Numeric, default=-1)
    unity = Column(Integer, default=0)
    initial_quantity = Column(Numeric, default=1)
    automatic_decrease = Column(Numeric, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'material'
    }

class Asset(Base):
    """
        * provider_id : from whom it was bought
        * acquisition_date
        * acquisiton_price
        * serial_number : odontux unique identifiant
        * new : true if the product is new
        * user : which user is using this asset 
        * office : to which dental office is related the asset
        * end_use_reason : 
            0 or None : in stock or in use.
            1 : Natural end of the material
            2 : Unconvenient
            3 : Obsolete/Out of date (périmé)
            4 : Removed from market
            5 : Lost
    """
    __tablename__ = "asset"
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey(AssetProvider.id), nullable=False)
    provider = relationship('AssetProvider')
    asset_category_id = Column(Integer, ForeignKey(AssetCategory.id), 
                                                                nullable=False)
    asset_category = relationship('AssetCategory')
    acquisition_date = Column(Date, default=func.current_date())
    acquisition_price = Column(Numeric, default=0)
    new = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
    user = relationship('users.OdontuxUser')
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id))
    office = relationship('users.DentalOffice')
    start_of_use = Column(Date, default=None)
    end_of_use = Column(Date, default=None)
    end_use_reason = Column(Integer, default=0)
    type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': type
    }
    
    def element_of_kit(self):
        query =  meta.session.query(AssetKit
                                    ).filter(AssetKit.end_of_use == None
                                    ).filter(AssetKit.end_use_reason == 0
                                    ).all()
        for q in query:
            for asset in q.assets:
                if asset.id == self.id:
                    return True
        return False
                                    
class Device(Asset):
    """
        * lifetime expected ; 0 if forever
    """
    __tablename__ = "device"
    id = Column(Integer, ForeignKey(Asset.id), primary_key=True)
    lifetime_expected = Column(Interval, default=None)

    __mapper_args__ = {
        'polymorphic_identity': 'device',
    }

class Material(Asset):
    """
        expiration_alert : default to two weeks
    """
    __tablename__ = "material"
    id = Column(Integer, ForeignKey(Asset.id), primary_key=True)
    used_in_traceability_of = Column(String)
    actual_quantity = Column(Numeric, default=1)
    expiration_date = Column(Date)
    expiration_alert = Column(Interval, default=datetime.timedelta(15))
    batch_number = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'material',
    }

class AssetKitStructure(Base):
    """
        This table will enable to create kits more easily.
        asset_category_id : Assets that may be include in this type of kit.
        This way, when we want to create a kit, only assets relevent are in
        the choice list.
    """
    __tablename__ = "asset_kit_structure"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    type_of_assets = relationship("AssetCategory", 
                                secondary=kitstructure_assetcategory_table,
                                backref="kits_structure")
    active = Column(Boolean, default=True)

class AssetKit(Base):
    """
        * end_use_reason : same as "Asset"
    """
    __tablename__ = "asset_kit"
    id = Column(Integer, primary_key=True)
    asset_kit_structure_id = Column(Integer, ForeignKey(AssetKitStructure.id), 
                                                                nullable=False)
    asset_kit_structure = relationship("AssetKitStructure")
    assets = relationship("Asset", secondary=kit_asset_table,
                                        backref="kits")
    creation_date = Column(Date, nullable=False)
    appointment_id = Column(Integer, ForeignKey(schedule.Appointment.id),
                                                           default=None)
    end_of_use = Column(Date, default=None)
    end_use_reason = Column(Integer, default=0)

