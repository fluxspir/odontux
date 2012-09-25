# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD

import sqlalchemy
from sqlalchemy import create_engine
import model
from model import meta


class CreateOdontuxDatabaseTool():
    """ """

    tool_name = "create_odontuxdb"

    def __init__(self):
        pass

    def run(self, args):
        model.init()
        meta.Base.metadata.create_all(bind=meta.session.bind.engine)
