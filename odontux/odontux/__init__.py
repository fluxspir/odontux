# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/23
# v0.5
# Licence BSD
#

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from model import meta


def main(global_config, **settings):
    """ This functions returns a WSGI application.
    """
    engine = engine_from_config(settings, "sqlalchemy.")
    meta.session.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
