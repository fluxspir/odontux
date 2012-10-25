# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from models import meta, headneck, teeth
from base import BaseTool

from sqlalchemy import and_, or_
from gettext import gettext as _
import sqlalchemy
import os
import sys


class GetToothTool(BaseTool):
    """ """

    tool_name = "get_toothid"

    def __init__(self):
        pass

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="id of the patient")
        parser.add_option("-n", "--name", action="store",\
                        type="string", dest="name",\
                        help="name of the tooth")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        if not options.name:
            sys.exit(_("Please tell tooth's name we're looking for"))

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        try:
            mouth_id = meta.session.query(headneck.Mouth)\
                    .filter(headneck.Mouth.patient_id == patient_id).one().id
        except sqlalchemy.orm.exc.NoResultFound:
            sys.exit(_("The mouth isn't in database yet"))

        query = meta.session.query(teeth.Tooth)\
                .filter(teeth.Tooth.mouth_id == mouth_id).all()
        for tooth in query:
            if tooth.name == options.name:
                print(_(tooth.id))
                sys.exit(tooth.id)
        print(_("The tooth isn't in database yet"))

class GetToothUnderSurveillanceTool(BaseTool):
    """ """
    
    tool_name = "get_toothundersurveillance"

    def __init__(self):
        self.teeth = meta.session.query(teeth.Tooth)
        self.mouth = meta.session.query(headneck.Mouth)

    def run(self, args):
        patient_id = os.getenv("patient_id")
        try:
            mouth_id = self.mouth.filter(
                            headneck.Mouth.patient_id == patient_id).one().id
        except sqlalchemy.orm.exc.NoResultFound:
            sys.exit(_("The mouth isn't in database yet"))

        toothmonitored = self.teeth.filter(and_(
                            teeth.Tooth.mouth_id == mouth_id,
                            teeth.Tooth.surveillance == True)
                            ).all()
        for tooth in toothmonitored:
            print(tooth.name)
            
