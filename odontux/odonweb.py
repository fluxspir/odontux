#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.5
# Licence BSD

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

from models import meta

from 

DEBUG = True
SECRET_KEY = "development key"
USERNAME = "admin"
PASSWORD = "default"

app = Flask(__name__)
app.config.from_object(__name__)


#@app.teardown_request
#def shutdown_session(exception=None):
#    meta.session.remove()

@app.route('/')
def index():
    return "odontux / odonweb"

if __name__ == "__main__":
    app.debug = DEBUG
    app.run()
