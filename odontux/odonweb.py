#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.5
# Licence BSD

from flask import Flask
from flask import Blueprint, g
import models
import checks

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
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['ODONTUX_FOLDER'] = checks.get_odontux_folder()
app.config['DOCUMENT_FOLDER'] = checks.get_odontux_document_folder()
app.config['THUMBNAIL_FOLDER'] = checks.get_thumbnail_folder()
app.config['LOCALE'] = checks.get_locale()

bp = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

models.init()

import odontux.views
