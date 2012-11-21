# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/28
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
from wtforms import (Form,
                     IntegerField, SelectField, TextField, BooleanField,
                     validators
                     )
from odontux.models import meta, anamnesis
from odontux.odonweb import app
from gettext import gettext as _

from odontux import constants

class MedicalHistoryForm(Form):
    
