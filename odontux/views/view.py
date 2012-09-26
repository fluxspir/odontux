# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/25
# v0.4
# Licence BSD
#

from pyramid.view import view_config

from ..models import meta, users

@view_config(route_name='home', renderer='templates/template.pt')
def my_view(request):
    one = meta.session.query(users.OdontuxUser)\
          .filter(users.OdontuxUser == 1).one()
    return {'one':one , 'project':'odontux'}
