#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.5
# Licence BSD

from flask import Flask
from flask import Blueprint, g
#from flask.ext.assets import Environment, Bundle
import models

from gettext import gettext as _
import sys

try:
    from secret import SECRET_KEY, USERNAME, PASSWORD
except:
    print(_("""Please create odontux/odontux/secret.py
with inside :

SECRET_KEY = "somethinghard2find93*9{];;;;eiir!!?|"
USERNAME = "username"
PASSWORD = "password"
"""))
    sys.exit(1)

DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)

#assets = Environment(app)
#pdf = Bundle('barcode.pdf')
#assets.register('pdf_all', pdf)

bp = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

models.init()

import odontux.views
