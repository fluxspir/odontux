# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from base import BaseCommand
from models import act, cotation, meta

from sqlalchemy import or_
from gettext import gettext as _
from decimal import Decimal
import sys

#getcontext().prec = 3

class CotationFrParser(BaseCommand):
    """ """

    def parse_args(self, args, update=False):
        """ """ 
        parser = self.get_parser()

        if update:
             parser.add_option("-c", "--cotation", action="store", 
                            type="string",
                            help="id of the cotation to upgrade",
                            dest="cotation_id")

        parser.add_option("-k", "--key", action="store", type="string",
                        help="CPAM Key letter for the act.",
                        dest="key_id")

        parser.add_option("--keycmu", action="store", type="string",
                        help="CMU Key letter for the act.",
                        dest="key_cmu_id")

        parser.add_option("-m", "--multiplicator", action="store",
                        type="string", dest="adult_multiplicator",
                        help="Multiplicator of the act.")

        parser.add_option("--kid_multiplicator", action="store", type="string",
                        help="Multiplicator of the act on a kid.",
                        dest="kid_multiplicator")

        parser.add_option("--adult_cmu_num", action="store", type="string",
                        help="Number for the key letter of the act",
                        dest="adult_cmu_num")

        parser.add_option("--kid_cmu_num", action="store", type="string",
                        help="Number for the key letter of the act, for kid",
                        dest="kid_cmu_num")

        parser.add_option("--exceeding_adult_normal", action="store",
                        type="string", dest="exceeding_adult_normal",
                        help="Exceeding, for an adult")

        parser.add_option("--exceeding_kid_normal", action="store",
                        type="string", dest="exceeding_kid_normal",
                        help="Exceeding, for a kid")

        parser.add_option("--exceeding_adult_cmu", action="store",
                        type="string", dest="exceeding_adult_cmu",
                        help="Exceeding, for an adult CMU")

        parser.add_option("--exceeding_kid_cmu", action="store",
                        type="string", dest="exceeding_kid_cmu",
                        help="Exceeding, for a kid CMU")

        parser.add_option("--totalprice_adult_normal", action="store",
                        type="string", dest="totalprice_adult_normal",
                        help="Total price for an adult normal")
                        
        parser.add_option("--totalprice_adult_cmu", action="store",
                        type="string", dest="totalprice_adult_cmu",
                        help="Total price for an adult cmu")

        (options, args) = parser.parse_args(args)
        return options, args


class AddNgapKeyFrCommand(BaseCommand):
    """
    NGAP is the codification of acts that can be done by medecine and dentist
    doctors.
    Each kind of act sees itself given a letter key, and a multiplicator.
    SC : soins conservateurs (operative dentistry) : unit_price = 2.41 euros
    SPR : soins prothetiques : unit price = 2.15 euros
    etc...
    """

    command_name = "add_ngapkeyfr"

    def __init__(self):
        self.values = {}

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-n", "--name", action="store",\
                        type="string", dest="name",\
                        help="name for the act.")
        parser.add_option("-k", "--key", action="store",\
                        type="string", dest="key",\
                        help="Key letter for the act.")
        parser.add_option("-p", "--price", action="store",\
                        type="string", dest="unit_price",\
                        help="Values of a unit of the letter_key.")

        (options,args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)

        self.values["name"] = options.name.decode("utf_8")
        self.values["key"] = options.key.decode("utf_8").upper()
        self.values["unit_price"] = options.unit_price.decode("utf_8")

        new_code = cotation.NgapKeyFr(**self.values)
        meta.session.add(new_code)

        meta.session.commit()


class AddCmuKeyFrCommand(BaseCommand):
    """
    Add into database CMU' special key letters, like:
    FDA : for prothese adjointe
    FDC pour la prothese conjointe...
    """
    command_name = "add_cmukeyfr"

    def __init__(self):    
        self.values = {}

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-n", "--name", action="store",\
                        type="string", dest="name",\
                        help="alias for the act.")
        parser.add_option("-k", "--key", action="store",\
                        type="string", dest="key",\
                        help="Code for the act.")

        (options,args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options,args) = self.parse_args(args)
        self.values["name"] = options.name.decode("utf_8")
        self.values["key"] = options.key.decode("utf_8").upper()

        new_code = cotation.CmuKeyFr(**self.values)
        meta.session.add(new_code)

        meta.session.commit()


class AddMajorationFrCommand(BaseCommand):
    """ """

    command_name = "add_majorationfr"

    def __init__(self):
        self.values = {}

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-n", "--name", action="store",\
                        type="string", dest="name",\
                        help="alias/name for the majoration.")
        parser.add_option("-p", "--price", action="store",\
                        type="string", dest="price",\
                        help="Majoration's price.")

        (options,args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options,args) = self.parse_args(args)
        
        self.values["name"] = options.name.decode("utf_8")
        self.values["price"] = options.price.decode("utf_8")

        new_majoration = cotation.MajorationFr(**self.values)
        meta.session.add(new_majoration)

        meta.session.commit()


class AddCotationFrCommand(BaseCommand, CotationFrParser):
    """ """

    command_name = "add_cotationfr"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)
        self.values["key_id"] = options.key_id.decode("utf_8")
        if options.key_cmu_id:
            self.values["key_cmu_id"] = options.key_cmu_id.decode("utf_8")
        if options.adult_multiplicator:
            self.values["adult_multiplicator"] = options.adult_multiplicator\
                                                        .decode("utf_8")
        if options.kid_multiplicator:
            self.values["kid_multiplicator"] = options.kid_multiplicator\
                                                      .decode("utf_8")
        else:
            self.values["kid_multiplicator"] = options.adult_multiplicator\
                                                      .decode("utf_8")
        if options.adult_cmu_num:
            self.values["adult_cmu_num"] = options.adult_cmu_num\
                                                  .decode("utf_8")
        if options.kid_cmu_num:    
            self.values["kid_cmu_num"] = options.kid_cmu_num.decode("utf_8")
        else:
            if options.adult_cmu_num:
                self.values["kid_cmu_num"] = options.adult_cmu_num\
                                                    .decode("utf_8")
        if options.exceeding_adult_normal:
            self.values["exceeding_adult_normal"] =\
                        options.exceeding_adult_normal.decode("utf_8")
        if options.exceeding_kid_normal:
            self.values["exceeding_kid_normal"] = options.exceeding_kid_normal\
                                                         .decode("utf_8")
        else:
            if options.exceeding_adult_normal:
                self.values["exceeding_kid_normal"] =\
                        options.exceeding_adult_normal.decode("utf_8")
        if options.exceeding_adult_cmu:
            self.values["exceeding_adult_cmu"] = options.exceeding_adult_cmu\
                                                        .decode("utf_8")
        if options.exceeding_kid_cmu:
            self.values["exceeding_kid_cmu"] = options.exceeding_kid_cmu\
                                                      .decode("utf_8")
        else:
            if options.exceeding_adult_cmu:
                self.values["exceeding_kid_cmu"] = options.exceeding_adult_cmu\
                                                          .decode("utf_8")

        new_cotation = cotation.CotationFr(**self.values)
        meta.session.add(new_cotation)

        meta.session.commit()
        print(new_cotation.id)


class ListNgapKeyFrCommand(BaseCommand):
    """ """

    command_name = "list_ngapkey"

    def __init__(self):
        self.query = meta.session.query(cotation.NgapKeyFr)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-k", "--key", action="store",\
                        type="string", dest="key",\
                        help="which key you wanna know the price")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        if options.key:
            keyword = '%{}%'.format(options.key)
            query = self.query.filter(cotation.NgapKeyFr.key.ilike(keyword))
        else:
            query = self.query

        for keycode in query:
            print(_(u"{} : {}\t{}\t{}"\
                .format(keycode.id, keycode.key, keycode.unit_price,
                keycode.name)))


class ListCmuKeyFrCommand(BaseCommand):
    """ """
    
    command_name = "list_cmukey"

    def __init__(self):
        self.query = meta.session.query(cotation.CmuKeyFr)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-k", "--key", action="store",\
                        type="string", dest="key",\
                        help="which key you wanna know the price")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        if options.key:
            keyword = '%{}%'.format(options.key)
            query = self.query.filter(cotation.NgapKeyFr.key.ilike(keyword))
        else:
            query = self.query

        for keycode in query:
            print(_(u"{} : {}\t{}"\
                .format(keycode.id, keycode.key, keycode.name)))


class ListCotationFrCommand(BaseCommand):
    """ """

    command_name = "list_cotationfr"

    def __init__(self):
        self.query = meta.session.query(cotation.CotationFr)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-s", "--specialty", action="store",\
                        type="string", dest="specialty_id",\
                        help="The specialty you're looking a cotation from")

        (options,args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options,args) = self.parse_args(args)
        if options.specialty_id:
            query = self.query\
                .filter(act.ActType.specialty_id == options.specialty_id)\
                .filter(act.ActType.cotationfr_id == cotation.CotationFr.id)
        else:
            query = self.query\
                .filter(act.ActType.cotationfr_id == cotation.CotationFr.id)
        
        if args:
            for keyword in args:
                keyword = '%{}%'.format(keyword)
                query = query.filter(or_(act.ActType.name.ilike(keyword),
                                    act.ActType.alias.ilike(keyword)))

        print(_(u"{} / {} | {}{} |   {}   |   {}   | {} || {} || {}"\
                    .format(_("Act id"), _("Key id"), _("keycode"), _("fr"),
                             _("SS"), _("TM"), _("Exceeding"), _("Total"),
                             _("Act name"))))


        for code in query:
            key = meta.session.query(cotation.NgapKeyFr)\
                        .filter(cotation.NgapKeyFr.id == code.key_id).one()
            description = meta.session.query(act.ActType)\
                    .filter(act.ActType.cotationfr_id == code.id)
            acte = meta.session.query(cotation.CotationFr).filter(
                                cotation.CotationFr.id == code.id).one()
            totalprice = acte.get_price(code.adult_multiplicator,
                                        code.exceeding_adult_normal)
            ngapprice = key.get_price(code.adult_multiplicator)
            ssprice = ngapprice * Decimal("0.7")
            tmprice = ngapprice - ssprice
            actekid = meta.session.query(cotation.CotationFr).filter(
                                cotation.CotationFr.id == code.id).one()
            totalpricekid = actekid.get_price(code.kid_multiplicator,
                                              code.exceeding_kid_normal)
            
            for desc in description:
                print(_(u" {}    /  {}      |    {}{}    | {} | \
{}  |    {}   ||   {}    ||    {}"\
                        .format(desc.id, code.id, key.key, 
                        code.adult_multiplicator, ssprice, tmprice,
                        code.exceeding_adult_normal, totalprice, desc.alias)))


class UpdateCotationFrCommand(BaseCommand, CotationFrParser):
    """ """

    command_name = "update_cotationfr"

    def __init__(self):
        self.query = meta.session.query(cotation.CotationFr)

    def run(self, args):
        (options, args) = self.parse_args(args, True)
        if not options.cotation_id:
            sys.exit(_("Please specify which cotation we need to upgrade"))
        newcotation = self.query.filter(cotation.CotationFr.id ==
                                        options.cotation_id).one()

        # key (SC, SPR ...)
        if options.key_id:
            newcotation.key_id = options.key_id.decode("utf_8")
        # cmu key (FDA, FDC ...)
        if options.key_cmu_id:
            newcotation.key_cmu_id = options.key_cmu_id.decode("utf_8")
        # multiplicators of keys
        if options.adult_multiplicator:
            newcotation.adult_multiplicator = \
            options.adult_multiplicator.decode("utf_8")
        if options.kid_multiplicator:
            newcotation.kid_multiplicator = \
            options.kid_multiplicator.decode("utf_8")
        else:
            if options.adult_multiplicator:
                newcotation.kid_multiplicator =\
                options.adult_multiplicator.decode("utf_8")
        if options.adult_cmu_num:
            newcotation.adult_cmu_num = \
            options.adult_cmu_num.decode("utf_8")
        if options.kid_cmu_num:    
            newcotation.kid_cmu_num = options.kid_cmu_num.decode("utf_8")
        else:
            if options.adult_cmu_num:
                newcotation.kid_cmu_num =\
                options.adult_cmu_num.decode("utf_8")
        # Exceeding
        if not options.totalprice_adult_normal:
            if options.exceeding_adult_normal:
                newcotation.exceeding_adult_normal =\
                options.exceeding_adult_normal.decode("utf_8")
            if options.exceeding_kid_normal:
                newcotation.exceeding_kid_normal =\
                options.exceeding_kid_normal.decode("utf_8")
            else:
                if options.exceeding_adult_normal:
                    newcotation.exceeding_kid_normal =\
                    options.exceeding_adult_normal.decode("utf_8")
            if options.exceeding_adult_cmu:
                newcotation.exceeding_adult_cmu =\
                options.exceeding_adult_cmu.decode("utf_8")
            if options.exceeding_kid_cmu:
                newcotation.exceeding_kid_cmu =\
                options.exceeding_kid_cmu.decode("utf_8")
            else:
                if options.exceeding_adult_cmu:
                    newcotation.exceeding_kid_cmu =\
                    options.exceeding_adult_cmu.decode("utf_8")
        else:
            multiplicator = newcotation.adult_multiplicator
            ngapprice = meta.session.query(cotation.NgapKeyFr)\
                        .filter(cotation.NgapKeyFr.id == newcotation.key_id)\
                        .one().get_price(multiplicator)
            exceeding_adult_normal = Decimal(options.totalprice_adult_normal)\
                                     - ngapprice
            newcotation.exceeding_adult_normal = exceeding_adult_normal
        meta.session.commit()
 
