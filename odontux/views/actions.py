# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/26
# v0.5
# Licence BSD
#

from odontux.odonweb import app
from flask import render_template

@app.route('/add/')
def add_generic():
    return render_template('add.html')

@app.route('/update/')
def update_generic():
    pass

@app.route('/list/')
def list_generic():
    pass
