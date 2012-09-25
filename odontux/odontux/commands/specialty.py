# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v 0.4
# Licence BSD
#

from base import BaseCommand
from model import act, meta

from sqlalchemy import or_
from gettext import gettext as _
import sys


class SpecialtyParser(BaseCommand):
     def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("-n", "--name", action="store",type="string",
                        help="Name of the specialty.",
                        dest="name")

        (options,args) = parser.parse_args(args)

        return options, args


class AddSpecialtyCommand(BaseCommand, SpecialtyParser):
    """ """

    command_name = "add_specialty"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        self.values["name"] = options.name.decode("utf_8")
        new_specialty = act.Specialty(**self.values)
        meta.session.add(new_specialty)

        meta.session.commit()


class ListSpecialtyCommand(BaseCommand, SpecialtyParser):
    """
    ./list_patient.py keyword1 keyword2
    will search for patient which lastname or firstname contains keyword
    """

    command_name = "list_specialty"

    def __init__(self):
        self.query = meta.session.query(act.Specialty)

    def run(self, args):
        (options, args) = self.parse_args(args)
        if options.name:
            keyword = '%{}%'.format(options.name)
            query = self.query.filter(act.Specialty.name.ilike(keyword))
        else:
            query = self.query

        for specialty in query:
            print(_(u"{}\t{}"\
                .format(specialty.id, specialty.name)))
