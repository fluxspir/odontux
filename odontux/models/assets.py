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
                    kitstructure_assetcategory_table,
                    superassetcategory_assetcategory_table,
                    superasset_asset_table)
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

"SuperAsset" is an Asset made by the fusion durable of various Asset.

"Kit" is a groupment of, generally, "Device". But a "Kit" may contain any 
type of Asset.

"""

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
    asset_specialty = relationship("act.Specialty")
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': type
    }

class DeviceCategory(AssetCategory):
    __tablename__ = "device_category"
    id = Column(Integer, ForeignKey(AssetCategory.id), primary_key=True)
    sterilizable = Column(Boolean, nullable=False)
    validity = Column(Interval, default=datetime.timedelta(90))
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
    provider_id = Column(Integer, ForeignKey(AssetProvider.id),
                                                        nullable=False)
    provider = relationship('AssetProvider')
    asset_category_id = Column(Integer, ForeignKey(AssetCategory.id), 
                                                        nullable=False)
    asset_category = relationship('AssetCategory')
    acquisition_date = Column(Date, default=func.current_date())
    acquisition_price = Column(Numeric, default=0, nullable=True)
    new = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
    user = relationship('users.OdontuxUser')
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id))
    office = relationship('users.DentalOffice')
    start_of_use = Column(Date, default=None)
    end_of_use = Column(Date, default=None)
    end_use_reason = Column(Integer, default=0)
    type = Column(String(20))
    sterilizations = relationship('AssetSterilized')

    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': type
    }

    def is_sterilizable(self):
        query = (
            meta.session.query(DeviceCategory)
                .filter(DeviceCategory.id == self.asset_category_id)
                .one_or_none().sterilizable
            )
        return query

    def element_of_kit(self):
        query = (
            meta.session.query(AssetKit)
                .filter(AssetKit.end_of_use.is_(None))
                .filter(AssetKit.end_use_reason == 0)
                .filter(AssetKit.appointment_id.is_(None))
                ).all()
        for q in query:
            for asset in q.assets:
                if asset.id == self.id:
                    return True
        return False
    
#    def is_sterilized(self):
#        if not self.is_sterilizable:
#            return None
#        query = (
#            meta.session.query(AssetSterilized)
#                .filter(AssetSterilized.asset_id == self.id)
#                .filter(AssetSterilized.appointment_id.is_(None))
#                .filter(AssetSterilized.expiration_date >
#                                                        func.current_date())
#                .one_or_none()
#            )
#        return query

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

class SuperAssetCategory(Base):
    """ """
    __tablename__ = "super_asset_category"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sterilizable = Column(Boolean, nullable=False)
    validity = Column(Interval, default=datetime.timedelta(90))
    superasset_specialty_id = Column(Integer, ForeignKey(act.Specialty.id))
    superasset_specialty = relationship("act.Specialty")
    type_of_assets = relationship("AssetCategory", 
                            secondary=superassetcategory_assetcategory_table,
                            backref="superasset_categories")

class SuperAsset(Base):
    """
        a super_asset is an asset made by addition of various assets
    """
    __tablename__ = "super_asset"
    id = Column(Integer, primary_key=True)
    superasset_category_id = Column(Integer, ForeignKey(SuperAssetCategory.id),
                                                                nullable=False)
    superasset_category = relationship("SuperAssetCategory")
    assets = relationship("Asset", secondary=superasset_asset_table,
                                            backref="superassets")
    creation_date = Column(Date, default=func.current_date())
    start_of_use = Column(Date, default=func.current_date())
    end_of_use = Column(Date, default=None)
    end_use_reason = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey(users.OdontuxUser.id))
    user = relationship('users.OdontuxUser')
    office_id = Column(Integer, ForeignKey(users.DentalOffice.id))
    office = relationship('users.DentalOffice')
    start_of_use = Column(Date, default=None)
    sterilizations  = relationship('AssetSterilized')

class AssetKitStructure(Base):
    """
        This table will enable to create kits more easily.
        type_of_assets : Assets that may be include in this type of kit.
        This way, when we want to create a kit, only assets relevent are in
        the choice list.
    """
    __tablename__ = "asset_kit_structure"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    type_of_assets = relationship("AssetCategory", 
                                secondary=kitstructure_assetcategory_table,
                                backref="kits_structure")
    validity = Column(Interval, default=datetime.timedelta(90))
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
    sterilization = relationship('AssetSterilized')

#    def is_sterilized(self):
#        query = (
#            meta.session.query(traceability.AssetSterilized)
#                .filter(AssetSterilized.kit_id == self.id)
#                .filter(AssetSterilized.appointment_id.is_(None))
#                .filter(AssetSterilized.expiration_date >
#                                                        func.current_date())
#                .one_or_none()
#            )
#        return query
 
