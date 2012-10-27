#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.5
# Licence BSD

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

from gettext import gettext as _
from models import meta
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

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


#@app.teardown_request
#def shutdown_session(exception=None):
#    meta.session.remove()

@app.route('/')
def index():
    return render_template('mytemplate.pt')

@app.route('/index.html')
def index_html():
    return "odontux"

@app.route('/suite/')
def index_html():
    return "suite"

if __name__ == "__main__":
    app.debug = DEBUG
    app.run()
