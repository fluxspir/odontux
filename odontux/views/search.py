# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# Licence BSD
#
import pdb
from flask import render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import or_
from odontux.models import (meta, act, administration, md, users, medication, 
                            assets, traceability )
from odontux.odonweb import app
from gettext import gettext as _
from odontux import constants
from odontux.views.act import list_gesture

@app.route('/search/', methods=['GET', 'POST'])
def find():
    """ """
    if request.form["database"] == "patient":
        keywords = request.form["keywords"].encode("utf_8").split()
        query = meta.session.query(administration.Patient)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                administration.Patient.lastname.ilike(keyword),
                administration.Patient.firstname.ilike(keyword),
                administration.Patient.preferred_name.ilike(keyword),
                administration.Patient.correspondence_name.ilike(keyword)
                )).order_by(administration.Patient.lastname)
        return render_template('list_patients.html', patients=query.all(),
                                role_admin=constants.ROLE_ADMIN)
    
    if request.form["database"] == "act":
        return redirect(url_for('list_gesture', 
                        keywords=request.form["keywords"],
                        ordering=" "))

    if request.form['database'] == "cotation":
        return redirect(url_for('list_cotations', 
                        keywords=request.form['keywords'].encode("utf_8"),
                        ordering=" "))

    if request.form["database"] == "odontuxuser":
        keywords = request.form["keywords"].encode("utf_8").split()
        query = meta.session.query(users.OdontuxUser)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                users.OdontuxUser.username.ilike(keyword),
                users.OdontuxUser.firstname.ilike(keyword),
                users.OdontuxUser.lastname.ilike(keyword),
                users.OdontuxUser.role.ilike(keyword)
                ))
        return render_template('list_users.html', users=query.all())

    if request.form["database"] == "doctor":
        keywords = request.form["keywords"].encode("utf_8").split()
        query = meta.session.query(md.MedecineDoctor)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                md.MedecineDoctor.lastname.ilike(keyword),
                md.MedecineDoctor.firstname.ilike(keyword),
                ))
        return render_template('list_md.html', doctors=query.all())

    if request.form["database"] == "drug":
        keywords = request.form["keywords"].encode("utf_8").split()
        query = meta.session.query(medication.DrugPrescribed)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                medication.DrugPrescribed.alias.ilike(keyword),
                medication.DrugPrescribed.molecule.ilike(keyword)
                ))
        return render_template('list_drugs.html', drugs=query.all())

    if request.form["database"] == "asset":
        keywords = request.form["keywords"].encode("utf_8").split()
        query_asset = (
            meta.session.query(assets.Asset)
                .join(assets.AssetCategory)
                .filter(assets.Asset.end_of_use == None,
                        assets.Asset.end_use_reason == 
                            constants.END_USE_REASON_IN_USE_STOCK
                )
            )
        query_superasset = (
            meta.session.query(assets.SuperAsset)
                .join(assets.SuperAssetCategory)
                .filter(assets.Asset.end_of_use == None,
                        assets.Asset.end_use_reason ==
                            constants.END_USE_REASON_IN_USE_STOCK
                )
            )

        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query_asset = query_asset.filter(or_(
                    assets.AssetCategory.brand.ilike(keyword),
                    assets.AssetCategory.commercial_name.ilike(keyword),
                    assets.AssetCategory.description.ilike(keyword),
                    ))
            query_superasset = query_superasset.filter(
                    assets.SuperAssetCategory.name.ilike(keyword)
                    )
        assets_list = []
        assets_to_render = ( query_asset
                    .join(act.Specialty)
                    .order_by(
                        act.Specialty.name,
                        assets.AssetCategory.brand,
                        assets.AssetCategory.commercial_name,
                        assets.Asset.start_of_use)
                    .all()
        )
        for asset in assets_to_render:
            assets_list.append(asset)
        for superasset in query_superasset.all():
            assets_list.append(superasset)
        return render_template('list_assets.html', assets_list=assets_list,
                                                    constants=constants)
 
    if request.form["database"] == "device":
        keywords = request.form["keywords"].encode("utf_8").split()
        query_device = (
            meta.session.query(assets.Device)
                .join(assets.DeviceCategory)
                .filter(assets.Device.end_of_use == None,
                        assets.Device.end_use_reason == 
                            constants.END_USE_REASON_IN_USE_STOCK
                )
            )
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query_device = query_device.filter(or_(
                    assets.DeviceCategory.brand.ilike(keyword),
                    assets.DeviceCategory.commercial_name.ilike(keyword),
                    assets.DeviceCategory.description.ilike(keyword),
                    ))
        assets_list = []
        assets_to_render = ( query_device
                    .join(assets.DeviceCategory, act.Specialty)
                    .order_by(
                        act.Specialty.name,
                        assets.DeviceCategory.brand,
                        assets.DeviceCategory.commercial_name,
                        assets.Device.start_of_use)
                    .all()
        )
        for asset in assets_to_render:
            assets_list.append(asset)
        return render_template('list_assets.html', assets_list=assets_list,
                                                    constants=constants)
        
    if request.form["database"] == "material":
        keywords = request.form["keywords"].encode("utf_8").split()
        query_material = (
            meta.session.query(assets.Material)
                .join(assets.MaterialCategory)
                .filter(assets.Material.end_of_use == None,
                        assets.Material.end_use_reason == 
                            constants.END_USE_REASON_IN_USE_STOCK
                )
            )
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query_material = query_material.filter(or_(
                    assets.MaterialCategory.brand.ilike(keyword),
                    assets.MaterialCategory.commercial_name.ilike(keyword),
                    assets.MaterialCategory.description.ilike(keyword),
                    ))
        assets_list = []
        assets_to_render = ( query_material
                    .join(assets.MaterialCategory, act.Specialty)
                    .order_by(
                        act.Specialty.name,
                        assets.MaterialCategory.brand,
                        assets.MaterialCategory.commercial_name,
                        assets.Material.start_of_use)
                    .all()
        )
        for asset in assets_to_render:
            assets_list.append(asset)
        return render_template('list_assets.html', assets_list=assets_list,
                                                    constants=constants)
 
    if request.form['database'] == 'sterilized_asset':
        sterilized_id = int(request.form['keywords'])
        sterilized_asset = (
            meta.session.query(traceability.AssetSterilized)
                .filter(traceability.AssetSterilized.id == sterilized_id)
                .one_or_none()
                )
        if sterilized_asset.asset_id:
            return redirect(url_for('view_asset', 
                                    asset_id=sterilized_asset.asset_id))
        elif sterilized_asset.superasset_id:
            return redirect(url_for('view_asset',
                                    asset_id=sterilized_asset.superasset_id))
        elif sterilized_asset.kit_id:
            return redirect(url_for('view_kit',
                                    kit_id=sterilized_asset.kit_id))
        else:
            return redirect(url_for('view_sterilization_cycle',
                        ste_cycle_id=sterilized_asset.sterilization_cycle_id))

@app.route('/search/user')
def find_user():
    pass
