import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from odontux.models import (
    meta,
    users,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    meta.session.configure(bind=engine)
    meta.Base.metadata.create_all(engine)
    with transaction.manager:
#        model = MyModel(name='one', value=1)
#        DBSession.add(model)
        values_user = { "username" : "franck",
                "password" : "secret",
                "role" : 1,
                "lastname" : "labadille".upper(),
                "firstname" : "franck".title(),
                "title" : "Dr",
                }
        my_user = users.OdontuxUser(**values_user)
        meta.session.add(my_user)
