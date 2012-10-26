#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

DEBUG = True
SECRET_KEY = "development key"
USERNAME = "admin"
PASSWORD = "default"

app = Flask(__name__)
app.config.from_object(__name__)


