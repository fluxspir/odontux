# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD

import pdb

import sqlalchemy
from sqlalchemy import create_engine
import models
from models import meta, users


class CreateOdontuxDatabaseTool():
    """ """

    tool_name = "create_odontuxdb"

    def __init__(self):
        pass

    def run(self, args):
        models.init()
        meta.Base.metadata.create_all(bind=meta.session.bind.engine)
        
        query = meta.session.query(users.OdontuxUser)
        query = query.all()
        if not query:
            # create an admin user
            print("creating first user \"admin\"")
            admin_user = {
                "username": "admin",
                "password": "please_change_password",
                "role": 4,
                "lastname": "admin",
                "firstname": "admin",
                "title": "M",
            }
            new_admin = users.OdontuxUser(**admin_user)
            meta.session.add(new_admin)
            meta.session.commit()
            
