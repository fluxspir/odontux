# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/29
# v0.5
# Licence BSD
#

from flask import session, render_template, redirect, url_for, request

from odontux import constants
from odontux.odonweb import app
from odontux.views import controls, forms
from odontux.models import meta, teeth
from odontux.views.log import index


