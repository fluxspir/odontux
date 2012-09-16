# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#
#

from base import BaseCommand
from model import compta

from gettext import gettext as _


class PaymentTypeParser(Base):
    """ """
    def parse_args(self, args, update=False):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="id of the payment method",
                            dest="paymenttype_id")

        parser.add_option("-n", "--name", action="store", type="string",
                        help="Name of payment method",
                        dest="name")

        parser.add_option("-a", "--alias", action="store", type="string",
                        help="alias for payment method",
                        dest="alias")

        (options, args) = parser.parse_args(args)
        return options, args
   
class AddPaymentTypeCommand(Base, PaymentTypeParser):
    """ """

    command_name = "add_paymenttype"

    def __init__(self):
        values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)
        self.values["name"] = options.name.decode("utf_8")
        if options.alias:
            self.values["alias"] = options.alias.decode("utf_8")

        new_paymenttype = compta.PaymentType(**self.values)
        meta.session.add(new_paymenttype)
        meta.session.commit()

class UpdatePaymentTypeCommand(Base, PaymentTypeParser):
    """ """

    command_name = "update_paymenttype"

    def __init__(self):
        paymenttype = meta.session.query(compta.PaymentType)

    def run(self, args):
        (options, args) = self.parse_args(args, True)
        payment_type = self.paymenttype.filter(compta.PaymentType.id ==
                                               options.paymenttype_id)
        if options.name:
            payment_type.name = options.name.decode("utf_8")
        if options.alias:
            payment_type.alias = options.alias.decode("utf_8")

        meta.session.commit()


class PaymentParser(Base):
    """ """

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-a", "--amount", action="store", type="string",
                        help="Amount of money in that payment",
                        dest="amount")

        parser.add_option("-m", "--mean", action="store", type="string",
                        help="Mean's id (payment's type id) for this payment",
                        dest="mean_id")

        parser.add_option("--advance", action="store_true", default=False,
                        help="this payment is an advance",
                        dest="advance")

        parser.add_option("-c", "--comments", action="store", type="string",
                        help="Précision about this payment",
                        dest="comments")

        (options, args) = parser.parse_args(args)
        return options, args

class AddPaymentCommand(Base, PaymentParser):
    """ """
    
    command_name = "add_payment"

    def __init__(self):
        values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        self.values["amount"] = options.amount.decode("utf_8")
        self.values["mean_id"] = options.mean_id.decode("utf_8")
        self.values["advance"] = options.advance
        if options.comments:
            self.values["comments"] = options.comments.decode("utf_8")

        new_payment = compta.Payment(**values)
        meta.session.add(new_payment)
        meta.session.commit()
