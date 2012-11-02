# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# Licence BSD
#

from flask import render_template
import sqlalchemy
from odontux.models import meta, administration, users
from odontux.odonweb import app
from gettext import gettext as _

@app.route('/search/?db=<database>?pattern=<pattern>/')
def find_patient(database, pattern):
    if database == "patient":
        pass
#        database = administration.Patient
#        pat

#    query = meta.session.query(database).filter(database.

@app.route('/search/user')
def find_user():
    pass
