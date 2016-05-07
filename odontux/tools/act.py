# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from models import meta, act, administration
from base import BaseTool

from gettext import gettext as _
from sqlalchemy import or_
import os
import sys


class GetActPriceTool(BaseTool):
    """ """

    tool_name = "get_actprice"

    def __init__(self):
        pass

    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("-a", "--act", action="store",\
                        type="string", dest="act_id",\
                        help="the act we want to get the price")
        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="the patient for whom we're searching the act's\
                              price.")
        parser.add_option("-m", "--majoration", action="store",\
                        type="string", dest="majoration_id",\
                        help="majoration we have to add to the total price")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)
        if options.majoration_id:
            majoration = meta.session.query(cotation.MajorationFr)\
              .filter(cotation.MajorationFr.id == options.majoration_id).one()
            majoration = majoration.price
        else:
            majoration = 0

        if not options.act_id:
            sys.exit(_("Please enter the act id with option -a"))
        act = meta.session.query(cotation.CotationFr)\
                .filter(cotation.CotationFr.id == options.act_id).one()

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        patient = meta.session.query(administration.Patient)\
                .filter(administration.Patient.id == patient_id).one()

        if patient.age() < 13:
            multiplicator = act.kid_multiplicator
            exceeding = act.exceeding_kid_normal
        else:
            multiplicator = act.adult_multiplicator
            exceeding = act.exceeding_adult_normal

        #if patient.cmu is True:
        #    exceeding = act.exceeding_adult_cmu
        #
        price = act.get_price(multiplicator, exceeding, majoration)
        print(price)


class GetActTypeIdTool(BaseTool):
    """ """

    tool_name = "get_acttypeid"

    def __init__(self):
        self.query = meta.session.query(act.ActType)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-s", "--specialty", action="store",\
                        type="string", dest="specialty_id",\
                        help="Specialty of the act we're looking for")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)
        if options.specialty_id:
            query = self.query.filter(act.ActType.specialty_id == 
                                      options.specialty_id)
        else:
            query = self.query

        for keyword in args:
            keyword = "%{}%".format(keyword)
            query = query.filter(or_(
                        act.ActType.name.ilike(keyword),
                        act.ActType.alias.ilike(keyword)
                        )
                    )
        
        query = query.first()
        if query:
            print(_(u"{}".format(query.id).encode("utf_8")))

class GetActCotationFrIdTool(BaseTool):
    """ """

    tool_name = "get_actcotationfrid"

    def __init__(self):
        self.query = meta.session.query(act.ActType)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-s", "--specialty", action="store",\
                        type="string", dest="specialty_id",\
                        help="Specialty of the act we're looking for")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        query = self.query
        for keyword in args:
            keyword = "%{}%".format(keyword)
            query = query.filter(or_(
                        act.ActType.name.ilike(keyword),
                        act.ActType.alias.ilike(keyword)))
        
        act_id = query.first()
        print(act_id.cotationfr_id)
