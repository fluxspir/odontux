# Franck Labadille
# 2012/08/25
# v0.4
# Licence BSD
#

from models import anamnesis, meta
from base import BaseCommand

from gettext import gettext as _
from sqlalchemy import or_
import os
import sys

class MedecineDoctorParser(BaseCommand):
    """ """
    def parse_args(self, args, update=False):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="the md id",
                            dest="md_id")

        parser.add_option("-l", "--lastname", action="store", type="string",
                          help="Lastname of the generalist doctor to add,"
                                                                " mandatory",
                          dest="lastname")

        parser.add_option("-f", "--firstname", action="store", type="string",
                          help="Firstname of generalist doctor.",
                          dest="firstname")

        parser.add_option("-c", "--city", action="store", type="string",
                          help="City where the generalist doctor works.",
                          dest="city")

        parser.add_option("-a", "--address", action="store", type="string",
                          help="Address of the generalist doctor office.",
                          dest="address")

        parser.add_option("-p", "--phone", action="store", type="string",
                          dest="phone", help="Phone of the generalist doctor.")

        parser.add_option("-m", "--mail", action="store", type="string",
                          help="Email address of the generalist doctor.",
                          dest="mail")

        (options,args) = parser.parse_args(args)

        return options, args


class AddMedecineDoctorCommand(BaseCommand, MedecineDoctorParser):
    """ """

    command_name = "add_md"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        if not options.lastname:
            sys.exit("a lastname must be provide to add "
                     "a new medecine doctor, please")

        self.values["lastname"] = options.lastname.decode("utf_8").upper()
        if options.firstname:
            self.values["firstname"] = options.firstname.decode("utf8").title()
        if options.city:
            self.values["city"] = options.city.decode("utf_8").title()
        if options.address:
            self.values["address"] = options.address.decode("utf_8").title()
        if options.phone:
            self.values["phone"] = options.phone.decode("utf_8")
        if options.mail:
            self.values["mail"] = options.mail.decode("utf_8").lower()

        new_generalist = MedecineDoctor(**self.values)

        meta.session.add(new_generalist)

        meta.session.commit()


class ListMedecineDoctorCommand(BaseCommand):
    """ """

    command_name = "list_md"

    def __init__(self):
        self.query = meta.session.query(MedecineDoctor)

    def parse_args(self, args):
        parser = self.get_parser()
    
        parser.add_option("-i", "--id", action="store_true", dest="md_id",
                        help="use this option if you want to get only the id")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        query = self.query
        if args:
            for keyword in args:
                keyword = '%{}%'.format(keyword)
                query = query.filter(or_(\
                                MedecineDoctor.lastname.ilike(keyword),
                                MedecineDoctor.firstname.ilike(keyword),
                                MedecineDoctor.city.ilike(keyword)))

        if options.md_id:
            query = query.one()
            print(u"{}".format(query.id))
        else:
            for doc in query:
                print(u"{}. {} {},\t{}".format(doc.id, doc.lastname,
                                           doc.firstname, doc.city))


class UpdateMedecineDoctorCommand(BaseCommand, MedecineDoctorParser):
    """ """

    command_name = "update_md"

    def __init__(self):
        self.query = meta.session.query(MedecineDoctor)

    def run(self, args):
        (options, args) = self.parse_args(args, True)

        if not options.md_id:
            sys.exit("the id of md must be provide to update md")

        doc = self.query.filter(MedecineDoctor.id ==
                                options.md_id).one()

        if options.lastname:
            doc.lastname = options.lastname.decode("utf_8").upper()
        if options.firstname:
            doc.firstname = options.firstname.decode("utf8").title()
        if options.city:
            doc.city = options.city.decode("utf_8").title()
        if options.address:
            doc.address = options.address.decode("utf_8").title()
        if options.phone:
            doc.phone = options.phone.decode("utf_8")
        if options.mail:
            doc.mail = options.mail.decode("utf_8").lower()

        meta.session.commit()


class MedicalHistoryParser(BaseCommand):
    """ """
    def parse_args(self, args, update=""):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="Medical history id we want to update",
                            dest="medicalhistory_id")

        parser.add_option("--patient", action="store", type="string",
                          help="id of the patient, mandatory",
                          dest="patient_id")

        parser.add_option("-u", "--user", action="store", type="string",
                          help="id dentist who did anamnesis",
                          dest="dentist_id")

        parser.add_option("-i", "--icd10", action="store", type="string",
                          dest="icd10", help="ICD10 code")

        parser.add_option("-d", "--disease", action="store", type="string",
                          dest="disease", help="A disease name")

        parser.add_option("--disorder", action="store", type="string",
                          dest="disorder", help="Disorder description")

        parser.add_option("--habitus", action="store", type="string",
                          dest="habitus", help="Patient's habitus")

        parser.add_option("-t", "--treatment", action="store", type="string",
                          help="Treatment used for this disease.",
                          dest="treatment")

        parser.add_option("--date", "--timestamp", action="store",
                          help="Date the disease/treatment begun",
                          type="string", dest="time_stamp")

        (options,args) = parser.parse_args(args)

        return options, args

class PastSurgeriesParser(BaseCommand):
    """ """

    def parse_args(self, args, update=""):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="Medical history id we want to update",
                            dest="pastsurgeries_id")

        parser.add_option("--patient", action="store", type="string",
                          help="id of the patient, mandatory",
                          dest="patient_id")

        parser.add_option("-u", "--user", action="store", type="string",
                          help="id of dentist who made anamnesis",
                          dest="dentist_id")

        parser.add_option("-s", "--surgery", action="store", type="string",
                          dest="surgery", help="Surgery the patient had.")

        parser.add_option("-p", "--problem", action="store",
                          help="Problem which happened during the surgery.",
                          type="string", dest="problem")

        parser.add_option("-c", "--complication", action="store",
                          help="Complication that occured after the surgery",
                          type="string", dest="complication")

        parser.add_option("-d", "--date", action="store", type="string",
                          dest="time_stamp", help="Year the surgery happened")

        (options,args) = parser.parse_args(args)
        return options, args


class AllergiesParser(BaseCommand):
    """ """

    def parse_args(self, args, update=""):

        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="Medical history id we want to update",
                            dest="allergies_id")

        parser.add_option("--patient", action="store", type="string",
                          help="id of the patient, mandatory",
                          dest="patient_id")

        parser.add_option("-u", "--user", action="store", type="string",
                          help="id of dentist who made anamnesis",
                          dest="dentist_id")

        parser.add_option("-d", "--drug", action="store", type="string",
                          dest="drug", help="Allergies to drugs.")

        parser.add_option("-m", "--metal", action="store", type="string",
                          dest="metal", help="Allergies to metals.")

        parser.add_option("-f", "--food", action="store", type="string",
                          dest="food", help="Allergies to food.")

        parser.add_option("-o", "--other", action="store", type="string",
                          dest="other", help="Allergies to other stuffs")

        parser.add_option("-r", "--reaction", action="store", type="string",
                          help="Type of reaction this allergens creates",
                          dest="reaction")

        parser.add_option("-t", "--date", "--timestamp", action="store",
                          type="string", dest="time_stamp",
                          help="when the allergie begun")

        (options,args) = parser.parse_args(args)
        return options, args


class AddMedicalHistoryCommand(BaseCommand, MedicalHistoryParser):
    """ """

    command_name = "add_medicalhistory"

    def __init__(self):
        self.values = {}

    def run(self, args):
        
        (options, args) = self.parse_args(args)

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        self.values["patient_id"] = patient_id
        self.values["dentist_id"] = options.dentist_id
        if options.icd10:
            self.values["icd10"] = options.icd10.decode("utf_8").upper()
        if options.disease:
            self.values["disease"] = options.disease.decode("utf_8").title()
        if options.disorder:
            self.values["disorder"] = options.disorder.decode("utf_8")
        if options.habitus:
            self.values["habitus"] = options.habitus.decode("utf_8")
        if options.treatment:
            self.values["treatment"] = options.treatment.decode("utf_8")
        if options.time_stamp:
            self.values["time_stamp"] = options.time_stamp.decode("utf_8")

        new_disease = anamnesis.MedicalHistory(**self.values)
        meta.session.add(new_disease)

        meta.session.commit()


class AddPastSurgeriesCommand(BaseCommand, PastSurgeriesParser):

    command_name = "add_surgeries"

    def __init__(self):
        self.values = {}

    def run(self, args):
        
        (options, args) = self.parse_args(args)

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        self.values["patient_id"] = patient_id
        self.values["dentist_id"] = options.dentist_id
        if options.surgery:
            self.values["surgery_type"] = options.surgery.decode("utf_8")
        if options.problem:
            self.values["problem"] = options.problem.decode("utf_8")
        if options.complication:
            self.values["complication"] = options.complication.decode("utf_8")
        if options.time_stamp:
            self.values["time_stamp"] = options.time_stamp

        new_surgery = anamnesis.PastSurgeries(**self.values)
        meta.session.add(new_surgery)

        meta.session.commit()


class AddAllergiesCommand(BaseCommand, AllergiesParser):

    command_name = "add_allergies"

    def __init__(self):
        self.values = {}

    def run(self, args):
        
        (options, args) = self.parse_args(args)

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        self.values["patient_id"] = patient_id
        self.values["dentist_id"] = options.dentist_id
        if options.drug:
            self.values["drug"] = options.drug.decode("utf_8")
        if options.metal:
            self.values["metal"] = options.metal.decode("utf_8")
        if options.food:
            self.values["food"] = options.food.decode("utf_8")
        if options.other:
            self.values["other"] = options.other.decode("utf_8")
        if options.reaction:
            self.values["reaction"] = options.reaction.decode("utf_8")
        if options.time_stamp:
            self.values["time_stamp"] = options.time_stamp

        new_allergy = anamnesis.Allergies(**self.values)
        meta.session.add(new_allergy)

        meta.session.commit()


class ListMedicalHistoryCommand(BaseCommand):
    """
    if started without options and without keywords, returns every diseases 
    (icd10) and treatment for patient in shell_variable.

    if started without options but with keywords : returns every patients which
    shows keywords in their icd10 and/or treatemnt.

    if started with options -d --disease keyword : returns patients which shows
    the disease

    if started with option -t --treatment : returns patients using this 
    treatment.
    """
    
    command_name = "list_medicalhistory"

    def __init__(self):
        self.query = meta.session.query(anamnesis.MedicalHistory)

    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="the patient id.")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        query = self.query.filter(anamnesis.MedicalHistory.patient_id == 
                                  patient_id)

        for keyword in args:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                            anamnesis.MedicalHistory.icd10.ilike(keyword),
                            anamnesis.MedicalHistory.disease.ilike(keyword),
                            anamnesis.MedicalHistory.disorder.ilike(keyword),
                            anamnesis.MedicalHistory.treatment.ilike(keyword),
                            anamnesis.MedicalHistory.habitus.ilike(keyword)
                            )
                    ).all()

        for q in query:
            print(_(u"{}.\t{}\t{}\t{}\t{}\t{}"
            .format(q.id, q.icd10, q.disease, q.disorder,q.treatment, 
                    q.habitus)))


class ListSurgeriesCommand(BaseCommand):
    """ """

    command_name = "list_surgeries"

    def __init__(self):
        self.query = meta.session.query(anamnesis.PastSurgeries)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="the patient id.")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        query = self.query.filter(anamnesis.PastSurgeries.patient_id == 
                                  patient_id)

        for keyword in args:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                        anamnesis.PastSurgeries.surgery_type.ilike(keyword),
                        anamnesis.PastSurgeries.complication.ilike(keyword),
                        anamnesis.PastSurgeries.problem.ilike(keyword)
                        )
                    ).all()

        for q in query:
            print(_(u"{}. {} {} {}"
                .format(q.id, q.surgery_type, q.complication, q.problem)
                )
             )


class ListAllergiesCommand(BaseCommand):
    """
    if started without options and without keywords, returns every allergies
    and treatment for patient in shell_variable.

    if started with options -d --drug keyword : returns patients which shows
    the 
    """

    command_name = "list_allergies"

    def __init__(self):
        self.query = meta.session.query(anamnesis.Allergies)

    def parse_args(self, args):

        parser = self.get_parser()
        parser.add_option("--id", action="store_true", default=False,
                        help="if we want to print only the allergy id",
                        dest="allergy_id")
        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="the patient id.")
        parser.add_option("-d", "--drug", action="store_true", dest="drug",\
                        help="drugs the patient is allergic to")
        parser.add_option("-m", "--metal", action="store_true", dest="metal",\
                        help="metal the patient is allergic to")
        parser.add_option("-f", "--food", action="store_true", dest="food",\
                        help="food the patient is allergic to")
        parser.add_option("-o", "--other", action="store_true", dest="other",\
                        help="other allergens for the patient")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        query = self.query.filter(anamnesis.Allergies.patient_id == patient_id)

            
        for keyword in args:
            keyword = '%{}%'.format(keyword)
            if options.drug:
                query = query.filter(anamnesis.Allergies.drug.ilike(keyword))
            elif options.metal:
                query = query.filter(anamnesis.Allergies.metal.ilike(keyword))
            elif options.food:
                query = query.filter(anamnesis.Allergies.food.ilike(keyword))
            elif options.other:
                query = query.filter(anamnenisl.Allergies.other.ilike(keyword))
            else:
                query = query.filter(or_(
                                    anamnesis.Allergies.drug.ilike(keyword),
                                    anamnesis.Allergies.metal.ilike(keyword),
                                    anamnesis.Allergies.food.ilike(keyword),
                                    anamnesis.Allergies.other.ilike(keyword),
                                    anamnesis.Allergies.reaction.ilike(keyword)
                                    )
                        )

        query = query.all()

        for allergy in query:
            if options.allergy_id:
                print(u"{}".format(allergy.id))
            else:
                print(u"{}. {} : {}\n{} : {}\n{} : {}\n{} : {}"\
                    .format(allergy.id, _("drug"), allergy.drug, _("metal"),
                    allergy.metal, _("food"), allergy.food, _("other"),
                    allergy.other))


class UpdateMedicalHistoryCommand(BaseCommand, MedicalHistoryParser):
    """ """

    command_name = "update_medicalhistory"

    def __init__(self):
        self.query = meta.session.query(anamnesis.MedicalHistory)

    def run(self, args):
        
        (options, args) = self.parse_args(args, True)

        if not options.medicalhistory_id:
            sys.exit(_("please specify the medical history id to update"))

        medhist = self.query.filter(anamnesis.MedicalHistory.id ==
                                    options.medicalhistory_id).one()

        if options.dentist_id:
            medhist.dentist_id = options.dentist_id.decode("utf_8")
        if options.icd10:
            medhist.icd10 = options.icd10.decode("utf_8").upper()
        if options.disease:
            medhist.disease = options.disease.decode("utf_8").title()
        if options.disorder:
            medhist.disorder = options.disorder.decode("utf_8")
        if options.habitus:
            medhist.habitus = options.habitus.decode("utf_8")
        if options.treatment:
            medhist.treatment = options.treatment.decode("utf_8")
        if options.time_stamp:
            medhist.time_stamp = options.time_stamp.decode("utf_8")

        meta.session.commit()


class UpdatePastSurgeriesCommand(BaseCommand, PastSurgeriesParser):

    command_name = "update_surgeries"

    def __init__(self):
        self.query = meta.session.query(anamnesis.PastSurgeries)

    def run(self, args):
        
        (options, args) = self.parse_args(args, True)

        if not options.pastsurgeries_id:
            sys.exit(_("please specify the past surgery id to update"))
       
        pastsurg = self.query.filter(anamnesis.PastSurgeries.id ==
                                    aptions.pastsurgeries_id).one()

        if options.dentist_id:
            pastsurg.dentist_id = options.dentist_id
        if options.surgery:
            pastsurg.surgery_type = options.surgery.decode("utf_8")
        if options.problem:
            pastsurg.problem = options.problem.decode("utf_8")
        if options.complication:
            pastsurg.complication = options.complication.decode("utf_8")
        if options.time_stamp:
            pastsurg.time_stamp = options.time_stamp

        meta.session.commit()


class UpdateAllergiesCommand(BaseCommand, AllergiesParser):

    command_name = "update_allergies"

    def __init__(self):
        self.query = meta.session.query(anamnesis.Allergies)

    def run(self, args):
        
        (options, args) = self.parse_args(args, True)

        if not options.allergies_id:
            sys.exit(_("Please specify allergy id you want to update"))
       
        allergy = self.query.filter(anamnesis.Allergies.id ==
                                    options.allergies_id).one()

        if options.dentist_id:
            allergy.dentist_id = options.dentist_id
        if options.drug:
            allergy.drug = options.drug.decode("utf_8")
        if options.metal:
            allergy.metal = options.metal.decode("utf_8")
        if options.food:
            allergy.food = options.food.decode("utf_8")
        if options.other:
            allergy.other = options.other.decode("utf_8")
        if options.reaction:
            allergy.reaction = options.reaction.decode("utf_8")
        if options.time_stamp:
            allergy.time_stamp = options.time_stamp

        meta.session.commit()
