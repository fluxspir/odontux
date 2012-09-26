import unittest
import transaction
import ConfigParser
import os

from pyramid import testing

from .models import meta

class TestMyView(unittest.TestCase):
    def setUp(self):
        # get url for database
        parser = ConfigParser.ConfigParser()
        home = os.path.expanduser("~")
        parser.read(os.path.join(home, ".odontuxrc"))
        db_url = parser.get("dbtest", "url")
        # ???
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        from .models import (
            tables
            users
            administration
            md
            anamnesis
            headneck
            softtissues
            periodonte
            teeth
            schedule
            medication
            act
            cotation
            compta
            )
        from constants import (
            ROLE_DENTIST,
            ROLE_NURSE,
            ROLE_ASSISTANT,
            ROLE_SECRETARY,
            ROLE_ADMIN
            )

        meta.session.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
#            model = MyModel(name='one', value=55)
#            DBSession.add(model)
            # Adding a odontuxuser
            values_user = { "username" : "franck",
                "password" : "secret",
                "role" : ROLE_DENTIST,
                "lastname" : "labadille".upper(),
                "firstname" : "franck".title(),
                "title" : "Dr",
                }


    def tearDown(self):
        meta.session.remove()
        testing.tearDown()

    def test_it(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'odontux')
