# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#
#

from base import BaseCommand
from model import compta

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

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


class ListPaymentTypeCommand(Base):
    """ """

    command_name = "list_paymenttype"

    def __init__(self):
        query = meta.session.query(compta.PaymentType)

    def parse_args(self, args):
        parser = self.get_parser()
        parser.add_option("--id", action="store_true", default=False,
                        help="Use this option to get only command type id",
                        desd="paymenttype_id")
        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        query = self.query
        for keyword in args:
            keyword = "%{}%".format(keyword)
            query = query.filter(or_(
                    compta.PaymentType.name.ilike(keyword),
                    compta.PaymentType.alias.ilike(keyword)))

        if options.paymenttype_id:
            try:
                paymenttype = query.one()
                print(paymenttype.id)
            except NoResultFound:
                sys.exit(_("No result found")
            except MultipleResultsFound:
                sys.exit(_("Multiple result found")
        else:
            paymenttypes = query.all()
            for p in paymenttypes:
                print(_("{}.\t{}\t{}"\
                        .format(p.id, p.name, p.alias)))

class PaymentParser(Base):
    """ """

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-p", "--payer", action="store", type="string",
                        help="Id of the patient who will pay the act",
                        dest="payer_id")
        
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

        parser.add_option("--cashin", action="store", type="string",
                        help="Date when the cash enters",
                        dest="cashin_date")

        (options, args) = parser.parse_args(args)
        return options, args

class AddPaymentCommand(Base, PaymentParser):
    """ """
    
    command_name = "add_payment"

    def __init__(self):
        values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        self.values["payer_id"] = options.payer_id.decode("utf_8")
        self.values["mean_id"] = options.mean_id.decode("utf_8")
        self.values["amount"] = options.amount.decode("utf_8")
        self.values["advance"] = options.advance
        if options.comments:
            self.values["comments"] = options.comments.decode("utf_8")
        if options.cashin_date:
            self.values["cashin_date"] = options.cashin_date

        new_payment = compta.Payment(**values)
        meta.session.add(new_payment)
        meta.session.commit()


class LinkPaymentActCommand(Base):
    """ """

    command_name = "link_paymentact"

    def __init__(self):
        query = meta.session.query(compta.Payment)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--act", action="store", type="string",
                        help="act id we're telling that was paid",
                        dest="act_id")

        parser.add_option("--payment", action="store", type="string",
                        help="payment id to link to act_id"
                        dest="payment_id")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)

        query = self.query.filter(compta.Payment.id ==
                           options.payment_id)

        payment = query.one()
        payment.acts_id.append(act.ActAppointmentReference(
                        act_id = options.act_id
                        ))
        meta.session.commit()
