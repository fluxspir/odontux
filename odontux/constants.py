# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

from gettext import gettext as _
import os
import datetime
import ConfigParser

parser = ConfigParser.ConfigParser()
home = os.path.expanduser("~")
parser.read(os.path.join(home, ".odontuxrc"))
LOCALE = parser.get("environment", "locale").lower()

if LOCALE == 'fr':
    CURRENCY_SYMBOL = u"€"
elif LOCALE == 'br':
    CURRENCY_SYMBOL = u"R$"
else:
    CURRENCY_SYMBOL = u"$"

QUOTE_VALIDITY = 2   # in months


T11_NAME = _("11") # _("Incisivo central superior right permanent")
T12_NAME = _("12") # _("Incisivo laterial superior right permanent")
T13_NAME = _("13") # _("Canina superior right permanent")
T14_NAME = _("14") # _("First Premolar superior right permanent")
T15_NAME = _("15") # _("Second Premolar superior right permanent")
T16_NAME = _("16") # _("First Molar superior right") 
T17_NAME = _("17") # _("Second Molar superior right permanent")
T18_NAME = _("18") # _("Third Molar superior right permanent")
T21_NAME = _("21") # _("Incisivo central superior left permanent")
T22_NAME = _("22") # _("Incisivo laterial superior left permanent")
T23_NAME = _("23") # _("Canina superior left permanent")
T24_NAME = _("24") # _("First Premolar laterial superior left permanent")
T25_NAME = _("25") # _("Second Premolar superior left permanent")
T26_NAME = _("26") # _("First Molar superior left") 
T27_NAME = _("27") # _("Second Molar superior left permanent")
T28_NAME = _("28") # _("Third Molar superior left permanent")
T31_NAME = _("31") # _("Incisivo central inferior left permanent")
T32_NAME = _("32") # _("Incisivo laterial inferior left permanent")
T33_NAME = _("33") # _("Canina inferior left permanent")
T34_NAME = _("34") # _("First Premolar inferior left permanent")
T35_NAME = _("35") # _("Second Premolar inferior left permanent")
T36_NAME = _("36") # _("First Molar inferior left") 
T37_NAME = _("37") # _("Second Molar inferior left permanent")
T38_NAME = _("38") # _("Third Molar inferior left permanent")
T41_NAME = _("41") # _("Incisivo central inferior right permanent")
T42_NAME = _("42") # _("Incisivo laterial inferior right permanent")
T43_NAME = _("43") # _("Canina inferior right permanent")
T44_NAME = _("44") # _("First Premolar inferior right permanent")
T45_NAME = _("45") # _("Second Premolar inferior right permanent")
T46_NAME = _("46") # _("First Molar inferior right") 
T47_NAME = _("47") # _("Second Molar inferior right permanent")
T48_NAME = _("48") # _("Third Molar inferior right permanent")
T51_NAME = _("51") # _("Incisivo central superior right deciduous")
T52_NAME = _("52") # _("Incisivo laterial superior right deciduous")
T53_NAME = _("53") # _("Canina superior right deciduous")
T54_NAME = _("54") # _("First Molar superior right deciduous")
T55_NAME = _("55") # _("Second Molar superior right deciduous")
T61_NAME = _("61") # _("Incisivo central superior left deciduous")
T62_NAME = _("62") # _("Incisivo laterial superior left deciduous")
T63_NAME = _("63") # _("Canina superior left deciduous")
T64_NAME = _("64") # _("First Molar superior left deciduous")
T65_NAME = _("65") # _("Second Molar superior left deciduous")
T71_NAME = _("71") # _("Incisivo central inferior left deciduous")
T72_NAME = _("72") # _("Incisivo laterial inferior left deciduous")
T73_NAME = _("73") # _("Canina inferior left deciduous")
T74_NAME = _("74") # _("First Molar inferior left deciduous")
T75_NAME = _("75") # _("Second Molar inferior left deciduous")
T81_NAME = _("81") # _("Incisivo central inferior right deciduous")
T82_NAME = _("82") # _("Incisivo laterial inferior right deciduous")
T83_NAME = _("83") # _("Canina inferior right deciduous")
T84_NAME = _("84") # _("First Molar inferior right deciduous")
T85_NAME = _("85") # _("Second Molar inferior right deciduous")

# ------------------------------------
# Odontux user
# ------------------------------------

ROLE_DENTIST = 1
ROLE_NURSE = 2
ROLE_ASSISTANT = 3
ROLE_SECRETARY = 4
ROLE_ADMIN = 5
ROLE_PATIENT = 6

ROLES = { ROLE_DENTIST: _("dentist"),
          ROLE_NURSE: _("nurse"),
          ROLE_ASSISTANT: _("assistant"),
          ROLE_SECRETARY: _("secretary"),
          ROLE_ADMIN: _("admin"),
          ROLE_PATIENT: _("patient"),
        }

KID_AGE = 13

PERIOD_MORNING = 1
PERIOD_AFTERNOON = 2
PERIOD_NIGHT = 3

PERIODS = {
    PERIOD_MORNING: _('Morning'),
    PERIOD_AFTERNOON: _('Afternoon'),
    PERIOD_NIGHT: _('Night')
}

# ------------------------------------
# Anamnesis
# ------------------------------------

HYGIENE_DENTIST = 1
HYGIENE_BRUSH = 2
HYGIENE_FLOSS = 3
HYGIENE_ANTISEPTICS = 4
HYGIENE_TOOTH_PASTE = 5

ORAL_HYGIENE = {
    HYGIENE_DENTIST: _('dentist'),
    HYGIENE_BRUSH: _('brush'),
    HYGIENE_FLOSS: _('dental floss'),
    HYGIENE_ANTISEPTICS: _('antiseptics'),
    HYGIENE_TOOTH_PASTE: _('toothpaste'),
    }

MEDICAL_HISTORY_DISEASE = 1
MEDICAL_HISTORY_DISORDER = 2
MEDICAL_HISTORY_HABITUS = 3

MEDICAL_HISTORIES = {
    MEDICAL_HISTORY_DISEASE: _('disease'),
    MEDICAL_HISTORY_DISORDER: _('disorder'),
    MEDICAL_HISTORY_HABITUS: _('habitus'),
    }

DISEASE_SANE = 0
DISEASE_BACTERIAL_INFECTION = 1
DISEASE_VIRAL_INFECTION = 2
DISEASE_FUNGAL_INFECTION = 3
DISEASE_CANCER = 4
DISEASE_CHRONIC_RENAL_FAILURE = 5
DISEASE_CHRONIC_HEPATIC_FAILURE = 6
DISEASE_CHRONIC_LUNG_FAILURE = 7
DISEASE_FAILURE = 8
DISEASE_ENDOCARDITIS = 9
DISEASE_HYPERTENSION = 10
DISEASE_DIABETE_TYPE_1 = 11
DISEASE_DIABETE_TYPE_2 = 12
DISEASE_DIABETE = 13
DISEASE_EMPHYSEMA = 14
DISEASE_CEREBROVASCULAR_ACCIDENT = 15

DISEASES = {
    DISEASE_SANE: _(''),
    DISEASE_BACTERIAL_INFECTION: _('bacterial infection'),
    DISEASE_VIRAL_INFECTION: _('viral infection'),
    DISEASE_FUNGAL_INFECTION: _('fungal infection'),
    DISEASE_CANCER: _('cancer'),
    DISEASE_CHRONIC_RENAL_FAILURE: _('chronic renal failure'),
    DISEASE_CHRONIC_HEPATIC_FAILURE: _('chronic hepatic failure'),
    DISEASE_CHRONIC_LUNG_FAILURE: _('chronic lung failure'),
    DISEASE_FAILURE: _('other failure'),
    DISEASE_ENDOCARDITIS: _('endocarditis'),
    DISEASE_HYPERTENSION: _('high blood pressure'),
    DISEASE_DIABETE_TYPE_1: _('diabete insulino-dependant'),
    DISEASE_DIABETE_TYPE_2: _('diabete no insulino-dependant'),
    DISEASE_DIABETE: _('other diabete'),
    DISEASE_EMPHYSEMA: _('Emphysema'),
    DISEASE_CEREBROVASCULAR_ACCIDENT: _('CerebroVascular Accident'),
    }

ADDICTION_TOBACCO = 0
ADDICTION_ALCOOL = 1
ADDICTION_MARIJUANA = 2
ADDICTION_HEROINA = 3
ADDICTION_COCAINA = 4
ADDICTION_OTHER = 999

ADDICTIONS = {
    ADDICTION_TOBACCO: _('tobacco'),
    ADDICTION_ALCOOL: _('alcool'),
    ADDICTION_MARIJUANA: _('marijuana'),
    ADDICTION_HEROINA: _('heroina'),
    ADDICTION_COCAINA: _('cocaina'),
    ADDICTION_OTHER: _('other'),
    }

ALLERGY_DRUG = 1
ALLERGY_METAL = 2
ALLERGY_FOOD = 3
ALLERGY_OTHER = 4

ALLERGIES = {
    ALLERGY_DRUG: _('drug'),
    ALLERGY_METAL: _('metal'),
    ALLERGY_FOOD: _('food'),
    ALLERGY_OTHER: _('other')
    }

ALLERGIC_REACTION_NONE = 0
ALLERGIC_REACTION_RUSH = 1
ALLERGIC_REACTION_QUINCKE = 2
ALLERGIC_REACTION_ANAPHYLAXIS = 3
ALLERGIC_REACTION_RHINITIS = 4

ALLERGIC_REACTIONS = {
    ALLERGIC_REACTION_NONE: ( _('none'), 'ALLERGIC_REACTION_NONE' ),
    ALLERGIC_REACTION_RUSH: ( _('cutaneous rush'), 'ALLERGIC_REACTION_RUSH' ),
    ALLERGIC_REACTION_QUINCKE: ( _('Quincke Edema'), 
                                                'ALLERGIC_REACTION_QUINCKE' ),
    ALLERGIC_REACTION_ANAPHYLAXIS: ( _('Anaphylaxis'), 
                                            'ALLERGIC_REACTION_ANAPHYLAXIS' ),
    ALLERGIC_REACTION_RHINITIS: ( _('allergic rhinitis'), 
                                                'ALLERGIC_REACTION_RHINITIS' ),
    }

ANAMNESIS_ANAMNESIS = 0
ANAMNESIS_MEDICAL_HISTORY = 1
ANAMNESIS_ADDICTION = 2
ANAMNESIS_TREATMENT = 3
ANAMNESIS_PAST_SURGERY = 4
ANAMNESIS_ALLERGY = 5
ANAMNESIS_ORAL_HYGIENE = 6

ANAMNESIS = {
    ANAMNESIS_MEDICAL_HISTORY: ( _('medical history'), 
                            'ANAMNESIS_MEDICAL_HISTORY', MEDICAL_HISTORIES ),
    ANAMNESIS_ADDICTION: ( _('addiction'), 'ANAMNESIS_ADDICTION', ADDICTIONS ),
    ANAMNESIS_TREATMENT: ( _('treatment'), 'ANAMNESIS_TREATMENT', None ),
    ANAMNESIS_PAST_SURGERY: ( _('past surgery'), 'ANAMNESIS_PAST_SURGERY', 
                                                                        None ),
    ANAMNESIS_ALLERGY: ( _('allergy'), 'ANAMNESIS_ALLERGY', ALLERGIES ),
    ANAMNESIS_ORAL_HYGIENE: ( _('oral hygiene'), 'ORAL_HIGIENE', 
                                                                ORAL_HYGIENE ),
    }

# ---------------------------------
# Anatomic location
# ---------------------------------

HEAD = 900
NECK = 910
SUPERIORLIP = 930
INFERIORLIP = 931
SUPERIOR_RIGHT_VESTIBULE = 923
SUPERIOR_CENTRAL_VESTIBULE = 924
SUPERIOR_LEFT_VESTIBULE = 925
INFERIOR_LEFT_VESTIBULE = 920
INFERIOR_CENTRAL_VESTIBULE = 927
INFERIOR_RIGHT_VESTIBULE = 928
LEFTCHEEK = 940
RIGHTCHEEK = 941
HARDPALATE = 950
SOFTPALATE = 951
UVULA = 952
TONGUE = 960
MOUTHBASE = 970

MOUTH = 0
A1 = MAXILLA = 1
A2 = MANDIBULA = 2
Q10 = QUADRANT_SUPERIOR_RIGHT = 10
Q20 = QUADRANT_SUPERIOR_LEFT = 20
Q30 = QUADRANT_INFERIOR_LEFT = 30
Q40 = QUADRANT_INFERIOR_RIGHT = 40
S03 = SEXTANT_SUPERIOR_RIGHT = 3
S04 = SEXTANT_SUPERIOR_CENTRAL = 4
S05 = SEXTANT_SUPERIOR_LEFT = 5
S06 = SEXTANT_INFERIOR_LEFT = 6
S07 = SEXTANT_INFERIOR_CENTRAL = 7
S08 = SEXTANT_INFERIOR_RIGHT = 8

T11 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_PERMANENT = 11
T12 = TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_PERMANENT = 12
T13 = TOOTH_CANINA_SUPERIOR_RIGHT_PERMANENT = 13
T14 = TOOTH_FIRST_PREMOLAR_SUPERIOR_RIGHT_PERMANENT = 14
T15 = TOOTH_SECOND_PREMOLAR_SUPERIOR_RIGHT_PERMANENT = 15
T16 = TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_PERMANENT = 16
T17 = TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_PERMANENT = 17
T18 = TOOTH_THIRD_MOLAR_SUPERIOR_RIGHT_PERMANENT = 18
T21 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_PERMANENT = 21
T22 = TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_PERMANENT = 22
T23 = TOOTH_CANINA_SUPERIOR_LEFT_PERMANENT = 23
T24 = TOOTH_FIRST_PREMOLAR_SUPERIOR_LEFT_PERMANENT = 24
T25 = TOOTH_SECOND_PREMOLAR_SUPERIOR_LEFT_PERMANENT = 25
T26 = TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_PERMANENT = 26
T27 = TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_PERMANENT = 27
T28 = TOOTH_THIRD_MOLAR_SUPERIOR_LEFT_PERMANENT = 28
T31 = TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_PERMANENT = 31
T32 = TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_PERMANENT = 32
T33 = TOOTH_CANINA_INFERIOR_LEFT_PERMANENT = 33
T34 = TOOTH_FIRST_PREMOLAR_INFERIOR_LEFT_PERMANENT = 34
T35 = TOOTH_SECOND_PREMOLAR_INFERIOR_LEFT_PERMANENT = 35
T36 = TOOTH_FIRST_MOLAR_INFERIOR_LEFT_PERMANENT = 36
T37 = TOOTH_SECOND_MOLAR_INFERIOR_LEFT_PERMANENT = 37
T38 = TOOTH_THIRD_MOLAR_INFERIOR_LEFT_PERMANENT = 38
T41 = TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_PERMANENT = 41
T42 = TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_PERMANENT = 42
T43 = TOOTH_CANINA_INFERIOR_RIGHT_PERMANENT = 43
T44 = TOOTH_FIRST_PREMOLAR_INFERIOR_RIGHT_PERMANENT = 44
T45 = TOOTH_SECOND_PREMOLAR_INFERIOR_RIGHT_PERMANENT = 45
T46 = TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_PERMANENT = 46
T47 = TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_PERMANENT = 47
T48 = TOOTH_THIRD_MOLAR_INFERIOR_RIGHT_PERMANENT = 48

PERMANENT_SUPERIOR_TEETH_SEQUENCE = ( 
                            TOOTH_THIRD_MOLAR_SUPERIOR_RIGHT_PERMANENT, 
                            TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_SECOND_PREMOLAR_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_FIRST_PREMOLAR_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_CANINA_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_PERMANENT,
                            TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_CANINA_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_FIRST_PREMOLAR_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_SECOND_PREMOLAR_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_PERMANENT,
                            TOOTH_THIRD_MOLAR_SUPERIOR_LEFT_PERMANENT
                            )

PERMANENT_INFERIOR_TEETH_SEQUENCE = (
                            TOOTH_THIRD_MOLAR_INFERIOR_LEFT_PERMANENT,
                            TOOTH_SECOND_MOLAR_INFERIOR_LEFT_PERMANENT,
                            TOOTH_FIRST_MOLAR_INFERIOR_LEFT_PERMANENT,
                            TOOTH_SECOND_PREMOLAR_INFERIOR_LEFT_PERMANENT,
                            TOOTH_FIRST_PREMOLAR_INFERIOR_LEFT_PERMANENT,
                            TOOTH_CANINA_INFERIOR_LEFT_PERMANENT,
                            TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_PERMANENT,
                            TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_PERMANENT,
                            TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_CANINA_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_FIRST_PREMOLAR_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_SECOND_PREMOLAR_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_PERMANENT,
                            TOOTH_THIRD_MOLAR_INFERIOR_RIGHT_PERMANENT
                            )

T51 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_DECIDUOUS = 51
T52 = TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_DECIDUOUS = 52
T53 = TOOTH_CANINA_SUPERIOR_RIGHT_DECIDUOUS = 53
T54 = TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_DECIDUOUS = 54
T55 = TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_DECIDUOUS = 55
T61 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_DECIDUOUS = 61
T62 = TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_DECIDUOUS = 62
T63 = TOOTH_CANINA_SUPERIOR_LEFT_DECIDUOUS = 63
T64 = TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_DECIDUOUS = 64
T65 = TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_DECIDUOUS = 65
T71 = TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_DECIDUOUS = 71
T72 = TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_DECIDUOUS = 72
T73 = TOOTH_CANINA_INFERIOR_LEFT_DECIDUOUS = 73
T74 = TOOTH_FIRST_MOLAR_INFERIOR_LEFT_DECIDUOUS = 74
T75 = TOOTH_SECOND_MOLAR_INFERIOR_LEFT_DECIDUOUS = 75
T81 = TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_DECIDUOUS = 81
T82 = TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_DECIDUOUS = 82
T83 = TOOTH_CANINA_INFERIOR_RIGHT_DECIDUOUS = 83
T84 = TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_DECIDUOUS = 84
T85 = TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_DECIDUOUS = 85

DECIDUOUS_SUPERIOR_TEETH_SEQUENCE = (
                            TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_DECIDUOUS,
                            TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_DECIDUOUS,
                            TOOTH_CANINA_SUPERIOR_RIGHT_DECIDUOUS,
                            TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_DECIDUOUS,
                            TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_DECIDUOUS,
                            TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_DECIDUOUS,
                            TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_DECIDUOUS,
                            TOOTH_CANINA_SUPERIOR_LEFT_DECIDUOUS,
                            TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_DECIDUOUS,
                            TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_DECIDUOUS,
                            )

DECIDUOUS_INFERIOR_TEETH_SEQUENCE = (
                            TOOTH_SECOND_MOLAR_INFERIOR_LEFT_DECIDUOUS,
                            TOOTH_FIRST_MOLAR_INFERIOR_LEFT_DECIDUOUS,
                            TOOTH_CANINA_INFERIOR_LEFT_DECIDUOUS,
                            TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_DECIDUOUS,
                            TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_DECIDUOUS,
                            TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_DECIDUOUS,
                            TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_DECIDUOUS,
                            TOOTH_CANINA_INFERIOR_RIGHT_DECIDUOUS,
                            TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_DECIDUOUS,
                            TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_DECIDUOUS,
                            )

ANATOMIC_LOCATION_SOFT_TISSUES = {
            HEAD: ( _("head"), str(HEAD), "headneck", "HeadEvent" ),
            NECK: ( _("neck"), str(NECK), "headneck", "NeckEvent" ),
            MOUTH: ( _("mouth"), str(MOUTH), "headneck", "MouthEvent" ),
            SUPERIOR_RIGHT_VESTIBULE: ( _('Vestibule Right Superior'), 
                                            str(SUPERIOR_RIGHT_VESTIBULE), 
                                            "endobuccal", "VestibuleEvent"),
            SUPERIOR_CENTRAL_VESTIBULE: ( _('Vestibule Central Superior'), 
                                            str(SUPERIOR_CENTRAL_VESTIBULE), 
                                            "endobuccal", "VestibuleEvent"),
            SUPERIOR_LEFT_VESTIBULE: ( _('Vestibule Left Superior'), 
                                            str(SUPERIOR_LEFT_VESTIBULE), 
                                            "endobuccal", "VestibuleEvent"),
            INFERIOR_LEFT_VESTIBULE: ( _('Vestibule Left Inferior'), 
                                            str(INFERIOR_LEFT_VESTIBULE),
                                            "endobuccal", "VestibuleEvent"),
            INFERIOR_CENTRAL_VESTIBULE: ( _('Vestibule Central Inferior'), 
                                            str(INFERIOR_CENTRAL_VESTIBULE),
                                            "endobuccal", "VestibuleEvent"),
            INFERIOR_RIGHT_VESTIBULE: ( _('Vestibule Right Inferior'), 
                                            str(INFERIOR_RIGHT_VESTIBULE),
                                            "endobuccal", "VestibuleEvent"),
            SUPERIORLIP: ( _("superior lip"), str(SUPERIORLIP), "endobuccal", 
                                                        "SuperiorLipEvent"),
            INFERIORLIP: ( _("inferior lip"), str(INFERIORLIP),"endobuccal", 
                                                        "InferiorLipEvent"),
            LEFTCHEEK: ( _("left cheek"), str(LEFTCHEEK),"endobuccal", 
                                                        "LeftCheekEvent"),
            RIGHTCHEEK: ( _("right cheek"), str(RIGHTCHEEK),"endobuccal", 
                                                        "RightCheekEvent"),
            HARDPALATE: ( _("hard palate"), str(HARDPALATE),"endobuccal", 
                                                        "HardPalateEvent"),
            SOFTPALATE: ( _("soft palate"), str(SOFTPALATE),"endobuccal", 
                                                        "SoftPalateEvent"),
            TONGUE: ( _("tongue"), str(TONGUE), "endobuccal", "TongueEvent"),
            MOUTHBASE: ( _("mouth base"), str(MOUTHBASE),"endobuccal", 
                                                            "MouthBaseEvent"),
            UVULA: ( _("palatine uvula"), str(UVULA), "endobuccal", 
                                                            "UvulaEvent"),
            }

ANATOMIC_LOCATION_TEETH_SET = {
            MAXILLA: ( _("maxillar"), str(MAXILLA), "teeth", 'Arcade'),
            MANDIBULA: ( _("mandibular"), str(MANDIBULA), "teeth", 'Arcade'),
            Q10: (_("quadrant superior right"), str(Q10), "teeth", "Quadrant"),
            Q20: (_("quadrant superior left"), str(Q20), "teeth", "Quadrant"),
            Q30: (_("quadrant inferior left"), str(Q30), "teeth", "Quadrant"),
            Q40: (_("quadrant inferior right"), str(Q40), "teeth", "Quadrant"),
            S03 : (_("sextant superior right"), str(S03), "teeth", "Sextant"),
            S04 : (_("sextant superior central"), str(S04), "teeth", "Sextant"),
            S05 : (_("sextant superior left"), str(S05), "teeth", "Sextant"),
            S06 : (_("sextant inferior left"), str(S06), "teeth", "Sextant"),
            S07 : (_("sextant inferior central"), str(S07), "teeth", "Sextant"),
            S08 : (_("sextant inferior right"), str(S08), "teeth", "Sextant"),
            }

ANATOMIC_LOCATION_TEETH = {
            T11: ( T11_NAME , str(T11), "teeth", "Tooth"),
            T12: ( T12_NAME , str(T12), "teeth", "Tooth"),
            T13: ( T13_NAME , str(T13), "teeth", "Tooth"),
            T14: ( T14_NAME , str(T14), "teeth", "Tooth"),
            T15: ( T15_NAME , str(T15), "teeth", "Tooth"),
            T16: ( T16_NAME , str(T16), "teeth", "Tooth"),
            T17: ( T17_NAME , str(T17), "teeth", "Tooth"),
            T18: ( T18_NAME , str(T18), "teeth", "Tooth"),
            T21: ( T21_NAME , str(T21), "teeth", "Tooth"),
            T22: ( T22_NAME , str(T22), "teeth", "Tooth"),
            T23: ( T23_NAME , str(T23), "teeth", "Tooth"),
            T24: ( T24_NAME , str(T24), "teeth", "Tooth"),
            T25: ( T25_NAME , str(T25), "teeth", "Tooth"),
            T26: ( T26_NAME , str(T26), "teeth", "Tooth"),
            T27: ( T27_NAME , str(T27), "teeth", "Tooth"),
            T28: ( T28_NAME , str(T28), "teeth", "Tooth"),
            T31: ( T31_NAME, str(T31), "teeth", "Tooth"),
            T32: ( T32_NAME, str(T32), "teeth", "Tooth"),
            T33: ( T33_NAME, str(T33), "teeth", "Tooth"),
            T34: ( T34_NAME, str(T34), "teeth", "Tooth"),
            T35: ( T35_NAME, str(T35), "teeth", "Tooth"),
            T36: ( T36_NAME, str(T36), "teeth", "Tooth"),
            T37: ( T37_NAME, str(T37), "teeth", "Tooth"),
            T38: ( T38_NAME, str(T38), "teeth", "Tooth"),
            T41: ( T41_NAME, str(T41), "teeth", "Tooth"),
            T42: ( T42_NAME, str(T42), "teeth", "Tooth"),
            T43: ( T43_NAME, str(T43), "teeth", "Tooth"),
            T44: ( T44_NAME, str(T44), "teeth", "Tooth"),
            T45: ( T45_NAME, str(T45), "teeth", "Tooth"),
            T46: ( T46_NAME, str(T46), "teeth", "Tooth"),
            T47: ( T47_NAME, str(T47), "teeth", "Tooth"),
            T48: ( T48_NAME, str(T48), "teeth", "Tooth"),
            T51: ( T51_NAME, str(T51), "teeth", "Tooth"),
            T52: ( T52_NAME, str(T52), "teeth", "Tooth"),
            T53: ( T53_NAME, str(T53), "teeth", "Tooth"),
            T54: ( T54_NAME, str(T54), "teeth", "Tooth"),
            T55: ( T55_NAME, str(T55), "teeth", "Tooth"),
            T61: ( T61_NAME, str(T61), "teeth", "Tooth"),
            T62: ( T62_NAME, str(T62), "teeth", "Tooth"),
            T63: ( T63_NAME, str(T63), "teeth", "Tooth"),
            T64: ( T64_NAME, str(T64), "teeth", "Tooth"),
            T65: ( T65_NAME, str(T65), "teeth", "Tooth"),
            T71: ( T71_NAME, str(T71), "teeth", "Tooth"),
            T72: ( T72_NAME, str(T72), "teeth", "Tooth"),
            T73: ( T73_NAME, str(T73), "teeth", "Tooth"),
            T74: ( T74_NAME, str(T74), "teeth", "Tooth"),
            T75: ( T75_NAME, str(T75), "teeth", "Tooth"),
            T81: ( T81_NAME, str(T81), "teeth", "Tooth"),
            T82: ( T82_NAME, str(T82), "teeth", "Tooth"),
            T83: ( T83_NAME, str(T83), "teeth", "Tooth"),
            T84: ( T84_NAME, str(T84), "teeth", "Tooth"),
            T85: ( T85_NAME, str(T85), "teeth", "Tooth"),
            }

TOOTH_STATE_SANE = 0
TOOTH_STATE_ILL = 1
TOOTH_STATE_PAIN = 2
TOOTH_STATE_HEALED = 3

TOOTH_STATE_MISPLACED = 5
TOOTH_STATE_MOBILE = 6
TOOTH_STATE_FRACTURE = 7
TOOTH_STATE_ABSENT = 8
TOOTH_STATE_RESIN = 10
TOOTH_STATE_IMPLANT = 11
TOOTH_WITHOUT_STATE = 20

TOOTH_STATES = {
            TOOTH_STATE_SANE: ( _("sane"), ),
            TOOTH_STATE_MISPLACED: ( _("misplaced"), ),
            TOOTH_STATE_MOBILE: ( _("mobile"), ),
            TOOTH_STATE_FRACTURE: ( _("fracture"), ),
            TOOTH_STATE_ABSENT: ( _("absent"), ),
            TOOTH_STATE_RESIN: ( _("resin"), ),
            TOOTH_STATE_IMPLANT: ( _("implant"), ),
            TOOTH_STATE_ILL: ( _("ill"), ),
            TOOTH_STATE_HEALED:( _('healed'), ),
            TOOTH_STATE_PAIN: ( _("pain"), ),
            TOOTH_WITHOUT_STATE: ( _("without_state"), ),
            }

CROWN_STATE_SANE = 0
CROWN_STATE_SEALING = 1
CROWN_STATE_OBTURATED = 2
CROWN_STATE_CROWNED = 3
CROWN_STATE_DECAYED = 4
CROWN_STATE_BRIDGE = 5

CROWN_STATES = {
            CROWN_STATE_SANE: ( _("sane"), ),
            CROWN_STATE_SEALING: ( _("sealing"), ),
            CROWN_STATE_OBTURATED: ( _("obturated"), ),
            CROWN_STATE_CROWNED: ( _("crowned"), ),
            CROWN_STATE_DECAYED: ( _("decayed"), ),
            CROWN_STATE_BRIDGE: ( _("bridge"), ),
           }

CROWN_SIDE_OCCLUSAL = 1
CROWN_SIDE_BUCCAL = 2
CROWN_SIDE_LINGUAL = 3
CROWN_SIDE_MESIAL = 4
CROWN_SIDE_DISTAL = 5 

CROWN_SIDES = {
            CROWN_SIDE_OCCLUSAL: ( _('O'), _("occlusal"), ),
            CROWN_SIDE_BUCCAL: ( _('B'), _("buccal"), ),
            CROWN_SIDE_LINGUAL: ( _('L'), _("lingual"), ),
            CROWN_SIDE_MESIAL: ( _('M'), _("mesial"), ),
            CROWN_SIDE_DISTAL: ( _('D'), _("distal"), ),
            }

ROOT_STATE_SANE = 0
ROOT_STATE_PULPOTOMIA = 1
ROOT_STATE_PULPECTOMIA = 2
ROOT_STATE_OBTURATED = 3
ROOT_STATE_INFECTED = 4
ROOT_STATE_APICAL_ABSCESS = 5
ROOT_STATE_POST_CORE = 6

ROOT_STATES = {
            ROOT_STATE_SANE: ( _("sane"), ),
            ROOT_STATE_PULPOTOMIA: ( _("pulpotomia"), ),
            ROOT_STATE_PULPECTOMIA: ( _("pulpectomia"), ),
            ROOT_STATE_OBTURATED: ( _("obturated"), ),
            ROOT_STATE_INFECTED: ( _("infected"), ),
            ROOT_STATE_APICAL_ABSCESS: ( _("apical abscess"), ),
            ROOT_STATE_POST_CORE: ( _("prosthetic core"), ),
            }

ROOT_CANAL_CENTRAL = 1
ROOT_CANAL_BUCCAL = 2
ROOT_CANAL_LINGUAL = 3
ROOT_CANAL_MESIAL = 4
ROOT_CANAL_DISTAL = 5 
ROOT_CANAL_MESIO_BUCCAL = 6
ROOT_CANAL_MESIO_LINGUAL = 7
ROOT_CANAL_DISTO_BUCCAL = 8
ROOT_CANAL_DISTO_LINGUAL = 9
ROOT_CANAL_MESIO_BUCCAL_2 = 10

ROOT_CANALS = {
            ROOT_CANAL_CENTRAL: ( _('C'), _("central"), ),
            ROOT_CANAL_BUCCAL: ( _('B'), _("buccal"), ),
            ROOT_CANAL_LINGUAL: ( _('L'), _("lingual"), ),
            ROOT_CANAL_MESIAL: ( _('M'), _("mesial"), ),
            ROOT_CANAL_DISTAL: ( _('D'), _("distal"), ),
            ROOT_CANAL_MESIO_BUCCAL: ( _('MB'), _("mesio-buccal"), ),
            ROOT_CANAL_MESIO_LINGUAL: ( _('ML'), _("mesio-lingual"), ),
            ROOT_CANAL_DISTO_BUCCAL: ( _('DB'), _("disto-buccal"), ),
            ROOT_CANAL_DISTO_LINGUAL: ( _('DL'), _("disto-lingual"), ),
            ROOT_CANAL_MESIO_BUCCAL_2: ( _('MB2'), _("mesio-buccal 2"), ),
}

PERIODONTAL_STATE_SANE = 0
PERIODONTAL_STATE_GINGIVITIS = 1
PERIODONTAL_STATE_PARODONTITIS = 2

PERIODONTAL_STATES = {
            PERIODONTAL_STATE_SANE: ( _('sane'), ),
            PERIODONTAL_STATE_GINGIVITIS: ( _('gingivitis'), ),
            PERIODONTAL_STATE_PARODONTITIS: ( _('parodontitis'), ),
            }

PERIODONTAL_LOC_MESIO_BUCCAL = 1
PERIODONTAL_LOC_BUCCAL = 2
PERIODONTAL_LOC_DISTO_BUCCAL = 3
PERIODONTAL_LOC_DISTO_LINGUAL = 4
PERIODONTAL_LOC_LINGUAL = 5
PERIODONTAL_LOC_MESIO_LINGUAL = 6

PERIODONTAL_LOCATIONS = {
            PERIODONTAL_LOC_MESIO_BUCCAL: ( _('MB'), _('mesio buccal') ),
            PERIODONTAL_LOC_BUCCAL: ( _('B'), _('buccal') ),
            PERIODONTAL_LOC_DISTO_BUCCAL: ( _('DB'), _('disto buccal') ),
            PERIODONTAL_LOC_DISTO_LINGUAL: ( _('DL'), _('disto lingual') ),
            PERIODONTAL_LOC_LINGUAL: ( _('L'), _('lingual') ),
            PERIODONTAL_LOC_MESIO_LINGUAL: ( _('ML'), _('mesio lingual') ),
            }

TOOTH_EVENT_LOCATION_TOOTH = 0
TOOTH_EVENT_LOCATION_CROWN = 1
TOOTH_EVENT_LOCATION_ROOT = 2
TOOTH_EVENT_LOCATION_PERIODONTAL = 3

TOOTH_EVENT_LOCATIONS = {
            TOOTH_EVENT_LOCATION_TOOTH: ( _("tooth"), 'tooth' ),
            TOOTH_EVENT_LOCATION_CROWN: ( _("crown"), 'crown' ),
            TOOTH_EVENT_LOCATION_ROOT: ( _("root"), 'root' ),
            TOOTH_EVENT_LOCATION_PERIODONTAL: (_("periodontal"),'periodontal'),
            }

# -------------------------------------------
# Assets
# -------------------------------------------

END_USE_REASON_IN_USE_STOCK = 0
END_USE_REASON_NATURAL_END = 1
END_USE_REASON_UNCONVENIENT = 2
END_USE_REASON_OBSOLETE = 3
END_USE_REASON_REMOVE_MARKET = 4
END_USE_REASON_LOST = 5

END_USE_REASONS = {
                END_USE_REASON_IN_USE_STOCK: ( _('In stock or in use'), 
                                                        'EUR_IN_USE_STOCK' ), 
                END_USE_REASON_NATURAL_END: ( _('Natural end of the asset'),
                                                        'EUR_NATURAL_END'),
                END_USE_REASON_UNCONVENIENT: ( _('Unconvenient'), 
                                                        'EUR_UNCONVENIENT' ),
                END_USE_REASON_OBSOLETE: ( _('Obsolete / Out of date'),
                                                        'EUR_OBSOLETE' ),
                END_USE_REASON_REMOVE_MARKET: ( _('Remove from market'),
                                                        'EUR_REMOVE_MARKET'), 
                END_USE_REASON_LOST: ( _('Lost'), 'EUR_LOST' ) 
               } 

UNITY_PIECE = 0
UNITY_VOLUME = 1
UNITY_WEIGHT = 2
UNITY_LENGTH = 3
UNITIES = {
            UNITY_PIECE: ( _("pieces/items"), _(""), 'UNITY_PIECE' ), 
            UNITY_VOLUME: ( _("volume in mL"), _("mL"), 'UNITY_VOLUME' ), 
            UNITY_WEIGHT: ( _("weight in gr"), _("gr"), 'UNITY_WEIGHT' ), 
            UNITY_LENGTH: ( _('length in m'), _("m"), 'UNITY_LENGTH' ),
        }

# --------------------------------------------------
# Files
# --------------------------------------------------

FILE_PHOTO = 2

FILE_PRESCRIPTION = 3

FILE_PRESENCE = 7
FILE_CESSATION = 8
FILE_REQUISITION = 9
REQUISITION_X_RAY = 90
REQUISITION_BIOLOGIC = 95 

REQUISITIONS = {
    REQUISITION_X_RAY: _('X ray'),
    REQUISITION_BIOLOGIC: _('Biologic'),
}

FILE_INVOICE = 20
FILE_QUOTE = 21
FILE_BILL = 22
FILE_RECEIPT = 23
if LOCALE == 'br':
    FILE_NOTA_FISCAL_PDF = 24
    FILE_NOTA_FISCAL_XML = 25

    NOTAS_FISCAIS = {
        FILE_NOTA_FISCAL_PDF: "Pdf",
        FILE_NOTA_FISCAL_XML: "XML",
    }

FILE_X_RAY_PERIAPICAL = 30
FILE_X_RAY_BITEWING = 31
FILE_X_RAY_OCCLUSAL = 32
FILE_X_RAY_PANORAMIC = 33
FILE_X_RAY_TELERADIO_FACE = 34
FILE_X_RAY_TELERADIO_PROFIL = 35

FILE_ANAMNESIS = 40

FILES = {
    FILE_PHOTO: ( _('Photo'), [ 'tooth' ] ),
    FILE_PRESCRIPTION: ( _('Prescription'), None ),
    FILE_PRESENCE: ( _('Presence'), [ 'certificate'] ),
    FILE_CESSATION: ( _('Cessation'), [ 'certificate' ] ),
    FILE_REQUISITION: (_('Requisition'), [ 'certificate' ] ),
    FILE_INVOICE: ( _('Invoice'), None ),
    FILE_QUOTE: ( _('Quote'), None ),
    FILE_BILL: ( _('Bill'), None ),
    FILE_RECEIPT: ( _('Receipt'), None ),
    FILE_X_RAY_PERIAPICAL: ( _('X_ray periapical'), [ 'tooth' ] ),
    FILE_X_RAY_BITEWING: ( _('X_ray bitewing'), [ 'tooth' ] ),
    FILE_X_RAY_OCCLUSAL: ( _('X_ray occlusal'), [ 'tooth' ] ),
    FILE_X_RAY_PANORAMIC: ( _('X_ray panoramic'), [ 'tooth', 'face' ] ),
    FILE_X_RAY_TELERADIO_FACE: ( _('X_ray teleradiography face'), [ 'face' ] ),
    FILE_X_RAY_TELERADIO_PROFIL: ( _('X_ray teleradiography profil'), 
                                                                [ 'face' ] ),
    FILE_ANAMNESIS: (_('Anamnesis'), None),
}

# ----------------------------------------------------------
# Gnucash
# ----------------------------------------------------------

GNUCASH_CURRENCY = 'BRL'

ASSETS = 'Assets'

RECEIVABLES = 'Patients Invoices'

DENTAL_FUND = 'Odontux Assets'

INCOMES = "Incomes"
DENTAL_INCOMES = "GestureToPay"

