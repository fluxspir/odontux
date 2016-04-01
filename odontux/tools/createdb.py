# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD

import pdb
from base64 import b64encode
import scrypt
import os

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
            print("password : please_change_password")
            print("Would be a great idea to change the admin password")
            admin_user = {
                "username": "admin",
                "password": b64encode(scrypt.encrypt(os.urandom(64),
                                        "please_change_password",
                                        maxtime=0.5)),
                "role": 4,
                "lastname": "admin",
                "firstname": "admin",
                "title": "M",
            }
            new_admin = users.OdontuxUser(**admin_user)
            meta.session.add(new_admin)
            meta.session.commit()
    
        query = meta.session.query(users.Settings)
        query = query.all()
        if not query:
            print('creating key-value for sticker_position')
            values = { 
                "key": "sticker_position",
                "value": "0"
                }
            new_setting = users.Settings(**values)
            meta.session.add(new_setting)
            meta.session.commit()
