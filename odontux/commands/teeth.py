# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from models import meta, teeth, headneck
from base import BaseCommand

from sqlalchemy import and_
from gettext import gettext as _
import sqlalchemy
import os
import sys
import constants

class EventParser(BaseCommand):
    """ """

    def parse_args(self, args, chunk):
        parser = self.get_parser()

        parser.add_option("--patient", action="store", type="string",
                        help="id of the patient, mandatory",
                        dest="patient_id")

        parser.add_option("--appointment", action="store", type="string",
                        help="appointment the event was recorded.",
                        dest="appointment_id")

        parser.add_option("--toothid", action="store", type="string",
                        help="the id of the tooth",
                        dest="tooth_id")

        parser.add_option("-n", "--name", action="store", type="string",
                        help="name of the tooth where an event is occuring",
                        dest="name")

        parser.add_option("-c", "--comments", action="store", type="string",
                        help="precision on what is happening",
                        dest="comments")
        
        parser.add_option("--color", action="store", type="string",
                        help="color of the event for the tooth",
                        dest="color")

        parser.add_option("--pic", "--img", action="store", type="string",
                        help="store path to pic",
                        dest="pic")
        
        parser.add_option("--surveillance", action="store_true", default=False,
                            help="keep an eye on this root",
                            dest="surveillance") 

        if chunk == "tooth":
            parser.add_option("-s", "--sane", action="store", type="string",
                            help="when the tooth looks healthy, but hurts",
                            dest="sane")

            parser.add_option("-p", "--place", action="store", type="string",
                            help="vest, pal...",
                            dest="place")

            parser.add_option("-m", "--mobility", action="store", 
                            type="string", dest="mobility",
                            help="tells the degree of mobility (1-2-3)")

            parser.add_option("-f", "--fracture", action="store", 
                            type="string", dest="fracture",
                            help="Radicular, Crown, or Rad-Crown")
                           
            parser.add_option("-a", "--absence", "--missing", action="store",
                            help="use it if the tooth is missing",
                            type="string",  dest="absence")

            parser.add_option("-r", "--replaced", action="store",
                            help="use it to tell the tooth was replaced",
                            type="string", dest="replaced")

            parser.add_option("-i", "--implant", action="store", type="string",
                            help="implant in the jaw",
                            dest="implant")

        if chunk == "crown":
            parser.add_option("-s", "--side", action="store", type="string",
                            help="The crown side : O, M, D, V/B, L/P or A(ll)",
                            dest="side")

            parser.add_option("--sealing", action="store", type="string",
                            help="Sealing",
                            dest="sealing")

            parser.add_option("-d", "--decay", action="store", type="string",
                            help="if the crown is decayed, black or sista",
                            dest="decay")

            parser.add_option("-o", "--obturation", action="store", 
                            type="string", dest="obturation",
                            help="the filling the tooth has")

            parser.add_option("-C", "--crown", action="store", type="string",
                            help="The type of crown",
                            dest="crowned")

            parser.add_option("-B", "--bridge", action="store", type="string",
                            help="There is a bridge",
                            dest="bridge")


        if chunk == "root":
            parser.add_option("-r", "--rootcanal", action="store", 
                            type="string", help="canal we're talking about",
                            dest="canal")

            parser.add_option("-i", "--infected", action="store",
                            help="tell what make think it's infected",
                            type="string", dest="infected")

            parser.add_option("-a", "--abscess", action="store", type="string",
                            help="to tell if there is an abscess",
                            dest="abscess")

            parser.add_option("-o", "--obturation", action="store", 
                            type="string", dest="obturation",
                            help="use it to tell that the root is filled")

            parser.add_option("-I", "--inlaycore", action="store", 
                            type="string", dest="inlaycore",
                            help="use of pilier in the root")
            parser.add_option("--screwpost", action="store",
                            type="string", dest="screwpost",
                            help="screw post in root")
  
        (options, args) = parser.parse_args(args)
        return options, args
            
class AddEventCommand(BaseCommand):
    """ """
    def add_mouth(self, patient_id):
        mouth_values = {}
        mouth_values["patient_id"] = patient_id
        new_mouth = headneck.Mouth(**mouth_values)
        meta.session.add(new_mouth)
        meta.session.commit()
        return new_mouth.id

    def add_tooth(self, mouth_id, name, state="s", surveillance=False):
        tooth_values = {}
        tooth_values["mouth_id"] = mouth_id
        tooth_values["name"] = name.decode("utf_8")
        if state:
            tooth_values["state"] = state.decode("utf_8")
        if surveillance:
            tooth_values["surveillance"] = True
        new_tooth = teeth.Tooth(**tooth_values)
        meta.session.add(new_tooth)
        meta.session.commit()
        return new_tooth.id


class AddToothEventCommand(BaseCommand, EventParser, AddEventCommand):
    """ """

    command_name = "add_toothevent"

    def __init__(self):
        self.event_values = {}
        self.toothevent_values = {}

    def run(self, args):

        (options,args) = self.parse_args(args, "tooth")
        
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")
        if options.name:
            name = options.name.decode("utf_8")
        else:
            sys.exit(_("Need to provide tooth name where event occured"))

        # in Class Toothevent
        self.event_values['location'] = constants.EVENT_LOCATION_TOOTH[0]
        if options.comments:
            self.event_values["comments"] = options.comments\
                                                        .decode("utf_8")
        if options.pic:
            self.event_values["pic"] = options.pic
        if options.color:
            self.event_values['color'] = options.color
        if options.appointment_id:
            self.event_values["appointment_id"] = options.appointment_id
        else:
            self.event_values["appointment_id"] =\
            os.getenv("appointment_id")
        if options.sane:
            state = "s"
            self.toothevent_values["sane"] = options.sane.decode("utf_8")
        if options.place:
            state = "p"
            self.toothevent_values["place"] = options.place.decode("utf_8")
        if options.mobility:
            state = "m" 
            self.toothevent_values["mobility"] =\
            options.mobility.decode("utf_8")
        if options.fracture:
            state = "f"
            self.toothevent_values["fracture"] =\
            options.fracture.decode("utf_8")
        if options.absence:
            state = "a"
            self.toothevent_values["absence"] = options.absence.decode("utf_8")
        if options.replaced:
            state = "r"
            self.toothevent_values["replaced"] = options.replaced\
                                                        .decode("utf_8")
        if options.implant:
            state = "I"
            self.toothevent_values["implant"] = options.implant.decode("utf_8")

        mouth = (
            meta.session.query(headneck.Mouth)
                .filter(headneck.Mouth.patient_id == patient_id)
        ).first()
        if mouth:
            mouth_id = mouth.id
        else:
            mouth_id = self.add_mouth(patient_id)

        tooth = (
            meta.session.query(teeth.Tooth)
                .filter(and_(teeth.Tooth.mouth_id == mouth_id,
                            teeth.Tooth.name == name))
        ).first()
        if not tooth:
            tooth_id = self.add_tooth(mouth_id, name, state, 
                                      options.surveillance)
        else:
            tooth_id = tooth.id
            tooth.state = state
            if options.surveillance:
                tooth.surveillance = True
            meta.session.commit()

        self.event_values["tooth_id"] = tooth_id
        new_event = teeth.Event(**self.event_values)
        meta.session.add(new_event)
        meta.session.commit()
        
        self.toothevent_values['event_id'] = new_event.id
        new_toothevent = teeth.ToothEvent(**self.toothevent_values)
        meta.session.add(new_toothevent)
        meta.session.commit()


class AddCrownEventCommand(BaseCommand, EventParser, AddEventCommand):
    """ """

    command_name = "add_crownevent"

    def __init__(self):
        self.event_values = {}
        self.crownevent_values = {}

    def run(self, args):

        (options, args) = self.parse_args(args, "crown")
        
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")
        if options.name:
            name = options.name.decode("utf_8")
        else:
            sys.exit(_("Need to provide tooth name where event occured"))

        # in Class Crownevent
        self.event_values['location'] = constants.EVENT_LOCATION_CROWN[0]
        if options.appointment_id:
            self.event_values["appointment_id"] = options.appointment_id
        else:
            self.event_values["appointment_id"] =\
            os.getenv("appointment_id")
        if options.comments:
            self.event_values["comments"] =\
            options.comments.decode("utf_8")
        if options.color:
            self.event_values["color"] = options.color.decode("utf_8")
        if options.pic:
            self.event_values["pic"] = options.pic

        self.crownevent_values["side"] = options.side.decode("utf_8")
        if options.sealing:
            state = "x"
            self.crownevent_values["sealing"] = options.sealing.decode("utf_8")
        if options.decay:
            state = "d"
            self.crownevent_values["decay"] = options.decay.decode("utf_8")
        if options.obturation:
            state = "o"
            self.crownevent_values["obturation"] =\
            options.obturation.decode("utf_8")
        if options.crowned:
            state = "c"
            self.crownevent_values["crowned"] = options.crowned.decode("utf_8")
        if options.bridge:
            state = "b"
            self.crownevent_values["bridge"] = options.bridge.decode("utf_8")

        mouth = (
            meta.session.query(headneck.Mouth)
                .filter(headneck.Mouth.patient_id == patient_id)
        ).first()
        if mouth:
            mouth_id = mouth.id
        else:
            mouth_id = self.add_mouth(patient_id)

        tooth = (
            meta.session.query(teeth.Tooth)
                .filter(and_(teeth.Tooth.mouth_id == mouth_id,
                            teeth.Tooth.name == name))
        ).first()
        if not tooth:
            tooth_id = self.add_tooth(mouth_id, name, state, 
                                      options.surveillance)
        else:
            tooth_id = tooth.id
            tooth.state = state
            if options.surveillance:
                tooth.surveillance = True
            meta.session.commit()

        self.event_values["tooth_id"] = tooth_id
        new_event = teeth.Event(**self.event_values)
        meta.session.add(new_event)
        meta.session.commit()

        self.crownevent_values['event_id'] = new_event.id
        new_crownevent = teeth.CrownEvent(**self.crownevent_values)
        meta.session.add(new_crownevent)
        meta.session.commit()


class AddRootEventCommand(BaseCommand, EventParser, AddEventCommand):
    """ """
    
    command_name = "add_rootevent"
    
    def __init__(self):
        self.event_values = {}
        self.rootevent_values = {}

    def run(self, args):

        (options,args) = self.parse_args(args, "root")
    
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        self.event_values['location'] = constants.EVENT_LOCATION_ROOT[0]
        if options.appointment_id:
            self.event_values["appointment_id"] = options.appointment_id
        else:
            self.event_values["appointment_id"] =\
            os.getenv("appointment_id")
        if options.comments:
            self.event_values["comments"] =\
            options.comments.decode("utf_8")
        if options.color:
            self.event_values["color"] = options.color
        if options.pic:
            self.event_values["pic"] = options.pic

        if options.name:
            name = options.name.decode("utf_8")
        else:
            sys.exit(_("Need to tell the tooth name where the event occured"))
        
        self.rootevent_values["canal"] = options.canal.decode("utf_8")
        if options.infected:
            self.rootevent_values["infected"] =\
            options.infected.decode("utf_8")
        if options.abscess:
            self.rootevent_values["abscess"] = options.abscess.decode("utf_8")
        if options.obturation:
            self.rootevent_values["obturation"] =\
            options.obturation.decode("utf_8")
        if options.inlaycore:
            self.rootevent_values["inlaycore"] =\
            options.inlaycore.decode("utf_8")
        if options.screwpost:
            self.rootevent_values["screwpost"] =\
            options.screwpost.decode("utf_8")

        mouth = (
            meta.session.query(headneck.Mouth)
                .filter(headneck.Mouth.patient_id == patient_id)
        ).first()

        if mouth:
            mouth_id = mouth.id
        else:
            mouth_id = self.add_mouth(patient_id)

        tooth = (
            meta.session.query(teeth.Tooth)
                .filter(and_(teeth.Tooth.mouth_id == mouth_id,
                            teeth.Tooth.name == name)
                )
        ).first()

        if not tooth:
            state=""
            tooth_id = self.add_tooth(mouth_id, name, state, 
                                      options.surveillance)
        else:
            if options.surveillance:
                tooth.surveillance = True
            tooth_id = tooth.id
            meta.session.commit()

        self.event_values["tooth_id"] = tooth_id
        new_event = teeth.Event(**self.event_values)
        meta.session.add(new_event)
        meta.session.commit()

        self.rootevent_values['event_id'] = new_event.id
        new_rootevent = teeth.RootEvent(**self.rootevent_values)
        meta.session.add(new_rootevent)
        meta.session.commit()


class ListPatientTeethCommand(BaseCommand):
    """ """
    
    command_name = "list_patientteeth"

    def __init__(self):
        self.teethdict = {}

    def run(self, args):
        patient_id = os.getenv("patient_id")

        try:
            mouth_id = meta.session.query(headneck.Mouth).filter(
                    headneck.Mouth.patient_id == patient_id).one().id
        except sqlalchemy.orm.exc.NoResultFound:
            print(_(u"toutes les dents sont présentes en bouche."
                    .encode("utf_8")))
            sys.exit(0)
        
        query = meta.session.query(teeth.Tooth)\
            .filter(teeth.Tooth.mouth_id == mouth_id).all()

        for tooth in query:
            self.teethdict[tooth.name] =\
            (tooth.id, tooth.state, tooth.surveillance)
            print(_(u"{}\t{} : {}\t{} : {}, {} : {}"
                    .format(tooth.id, _("name"), tooth.name, _("state"),
                            tooth.state, _("under surveillance"), 
                            tooth.surveillance)))
        return self.teethdict


class GetToothIdCommand(BaseCommand):
    """ """

    command_name = "get_toothid"

    def __init__(self):
        self.mouthquery = meta.session.query(headneck.Mouth)
        self.toothquery = meta.session.query(teeth.Tooth)

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
            mouth_id = self.mouthquery.filter(
                        headneck.Mouth.patient_id == patient_id).one().id
        except sqlalchemy.orm.exc.NoResultFound:
            sys.exit(_("The mouth isn't in database yet"))

        query = self.toothquery.filter(teeth.Tooth.mouth_id == mouth_id).all()

        for tooth in query:
            if tooth.name == options.name:
                print(_(tooth.id))
                sys.exit(0)
        print(_("The tooth isn't in database yet"))

