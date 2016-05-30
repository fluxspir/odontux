#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

from gettext import gettext as _
import ConfigParser
import os
import datetime

parser = ConfigParser.ConfigParser()
home = os.path.expanduser("~")
parser.read(os.path.join(home, ".odontuxrc"))
LOCALE = parser.get("environment", "locale").title()

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7

ISOWEEKDAYS = {
    MONDAY: _('Monday'),
    TUESDAY: _('Tuesday'),
    WEDNESDAY: _('Wednesday'),
    THURSDAY: _('Thursday'),
    FRIDAY: _('Friday'),
    SATURDAY: _('Saturday'),
    SUNDAY: _('Sunday'),
    }

JANUARY = 1
FEBRUARY = 2
MARCH = 3
APRIL = 4
MAY = 5
JUNE = 6
JULY = 7
AUGUST = 8
SEPTEMBER = 9
OCTOBER = 10
NOVEMBER = 11
DECEMBER = 12

MONTHS = {
    JANUARY: _("January"),
    FEBRUARY: _("February"),
    MARCH: _('March'),
    APRIL: _('April'),
    MAY: _('May'),
    JUNE: _('June'),
    JULY: _('July'),
    AUGUST: _('August'),
    SEPTEMBER: _('September'),
    OCTOBER: _('October'),
    NOVEMBER: _('November'),
    DECEMBER: _('December'),
    }
# ------------------------------------
# Odontux user
# ------------------------------------


ROLE_DENTIST = 0
ROLE_NURSE = 1
ROLE_ASSISTANT = 2
ROLE_SECRETARY = 3
ROLE_ADMIN = 4
ROLE_PATIENT = 5

ROLES = { ROLE_DENTIST: _("dentist"),
          ROLE_NURSE: _("nurse"),
          ROLE_ASSISTANT: _("assistant"),
          ROLE_SECRETARY: _("secretary"),
          ROLE_ADMIN: _("admin"),
          ROLE_PATIENT: _("patient"),
        }
ROLES_LIST = ROLES.items()  #ROLES_LIST = [(k, ROLES[k]) for k in ROLES.keys()]

KID_AGE = 13

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

ALLERGIC_REACTIONS = {
    ALLERGIC_REACTION_NONE: ( _('none'), 'ALLERGIC_REACTION_NONE' ),
    ALLERGIC_REACTION_RUSH: ( _('cutaneous rush'), 'ALLERGIC_REACTION_RUSH' ),
    ALLERGIC_REACTION_QUINCKE: ( _('Quincke Edema'), 
                                                'ALLERGIC_REACTION_QUINCKE' ),
    ALLERGIC_REACTION_ANAPHYLAXIS: ( _('Anaphylaxis'), 
                                            'ALLERGIC_REACTION_ANAPHYLAXIS' ),
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

T11 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_DEFINITIVE = 11
T12 = TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_DEFINITIVE = 12
T13 = TOOTH_CANINA_SUPERIOR_RIGHT_DEFINITIVE = 13
T14 = TOOTH_FIRST_PREMOLAR_SUPERIOR_RIGHT_DEFINITIVE = 14
T15 = TOOTH_SECOND_PREMOLAL_SUPERIOR_RIGHT_DEFINITIVE = 15
T16 = TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_DEFINITIVE = 16
T17 = TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_DEFINITIVE = 17
T18 = TOOTH_THIRD_MOLAR_SUPERIOR_RIGHT_DEFINITIVE = 18
T21 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_DEFINITIVE = 21
T22 = TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_DEFINITIVE = 22
T23 = TOOTH_CANINA_SUPERIOR_LEFT_DEFINITIVE = 23
T24 = TOOTH_FIRST_PREMOLAR_SUPERIOR_LEFT_DEFINITIVE = 24
T25 = TOOTH_SECOND_PREMOLAL_SUPERIOR_LEFT_DEFINITIVE = 25
T26 = TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_DEFINITIVE = 26
T27 = TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_DEFINITIVE = 27
T28 = TOOTH_THIRD_MOLAR_SUPERIOR_LEFT_DEFINITIVE = 28
T31 = TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_DEFINITIVE = 31
T32 = TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_DEFINITIVE = 32
T33 = TOOTH_CANINA_INFERIOR_LEFT_DEFINITIVE = 33
T34 = TOOTH_FIRST_PREMOLAR_INFERIOR_LEFT_DEFINITIVE = 34
T35 = TOOTH_SECOND_PREMOLAL_INFERIOR_LEFT_DEFINITIVE = 35
T36 = TOOTH_FIRST_MOLAR_INFERIOR_LEFT_DEFINITIVE = 36
T37 = TOOTH_SECOND_MOLAR_INFERIOR_LEFT_DEFINITIVE = 37
T38 = TOOTH_THIRD_MOLAR_INFERIOR_LEFT_DEFINITIVE = 38
T41 = TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_DEFINITIVE = 41
T42 = TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_DEFINITIVE = 42
T43 = TOOTH_CANINA_INFERIOR_RIGHT_DEFINITIVE = 43
T44 = TOOTH_FIRST_PREMOLAR_INFERIOR_RIGHT_DEFINITIVE = 44
T45 = TOOTH_SECOND_PREMOLAL_INFERIOR_RIGHT_DEFINITIVE = 45
T46 = TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_DEFINITIVE = 46
T47 = TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_DEFINITIVE = 47
T48 = TOOTH_THIRD_MOLAR_INFERIOR_RIGHT_DEFINITIVE = 48

DEFINITIVE_SUPERIOR_TEETH_SEQUENCE = ( 
                            TOOTH_THIRD_MOLAR_SUPERIOR_RIGHT_DEFINITIVE, 
                            TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_SECOND_PREMOLAL_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_FIRST_PREMOLAR_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_CANINA_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_DEFINITIVE,
                            TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_CANINA_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_FIRST_PREMOLAR_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_SECOND_PREMOLAL_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_DEFINITIVE,
                            TOOTH_THIRD_MOLAR_SUPERIOR_LEFT_DEFINITIVE
                            )

DEFINITIVE_INFERIOR_TEETH_SEQUENCE = (
                            TOOTH_THIRD_MOLAR_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_SECOND_MOLAR_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_FIRST_MOLAR_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_SECOND_PREMOLAL_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_FIRST_PREMOLAR_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_CANINA_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_DEFINITIVE,
                            TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_CANINA_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_FIRST_PREMOLAR_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_SECOND_PREMOLAL_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_DEFINITIVE,
                            TOOTH_THIRD_MOLAR_INFERIOR_RIGHT_DEFINITIVE
                            )

T51 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_TEMPORARY = 51
T52 = TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_TEMPORARY = 52
T53 = TOOTH_CANINA_SUPERIOR_RIGHT_TEMPORARY = 53
T54 = TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_TEMPORARY = 54
T55 = TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_TEMPORARY = 55
T61 = TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_TEMPORARY = 61
T62 = TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_TEMPORARY = 62
T63 = TOOTH_CANINA_SUPERIOR_LEFT_TEMPORARY = 63
T64 = TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_TEMPORARY = 64
T65 = TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_TEMPORARY = 65
T71 = TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_TEMPORARY = 71
T72 = TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_TEMPORARY = 72
T73 = TOOTH_CANINA_INFERIOR_LEFT_TEMPORARY = 73
T74 = TOOTH_FIRST_MOLAR_INFERIOR_LEFT_TEMPORARY = 74
T75 = TOOTH_SECOND_MOLAR_INFERIOR_LEFT_TEMPORARY = 75
T81 = TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_TEMPORARY = 81
T82 = TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_TEMPORARY = 82
T83 = TOOTH_CANINA_INFERIOR_RIGHT_TEMPORARY = 83
T84 = TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_TEMPORARY = 84
T85 = TOOTH_ECOND_MOLAR_INFERIOR_RIGHT_TEMPORARY = 85

ANATOMIC_LOCATION_SOFT_TISSUES = {
            HEAD: ( _("head"), str(HEAD), "headneck", "HeadEvent" ),
            NECK: ( _("neck"), str(NECK), "headneck", "NeckEvent" ),
            MOUTH: ( _("mouth"), str(MOUTH), "headneck", "MouthEvent" ),
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

ANATOMIC_LOCATION_TEETH = {
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
            T11: ( _("Incisivo central superior right"), str(T11), "teeth", "Tooth"),
            T12: ( _("Incisivo laterial superior right"), str(T12), "teeth", "Tooth"),
            T13: ( _("Canina superior right"), str(T13), "teeth", "Tooth"),
            T14: ( _("First Premolar superior right"), str(T14), "teeth", "Tooth"),
            T15: ( _("Second Premolar superior right"), str(T15), "teeth", "Tooth"),
            T16: ( _("First Molar superior right"), str(T16), "teeth", "Tooth"),
            T17: ( _("Second Molar superior right"), str(T17), "teeth", "Tooth"),
            T18: ( _("Third Molar superior right"), str(T18), "teeth", "Tooth"),
            T21: ( _("Incisivo central superior left"), str(T21), "teeth", "Tooth"),
            T22: ( _("Incisivo lateral superior left"), str(T22), "teeth", "Tooth"),
            T23: ( _("Canina superior left"), str(T23), "teeth", "Tooth"),
            T24: ( _("First Premolar superior left"), str(T24), "teeth", "Tooth"),
            T25: ( _("Second Premolar superior left"), str(T25), "teeth", "Tooth"),
            T26: ( _("First Molar superior left"), str(T26), "teeth", "Tooth"),
            T27: ( _("Second Molar superior left"), str(T27), "teeth", "Tooth"),
            T28: ( _("Third Molar superior left"), str(T28), "teeth", "Tooth"),
            T31: ( _("teeth"), str(T31), "teeth", "Tooth"),
            T32: ( _("teeth"), str(T32), "teeth", "Tooth"),
            T33: ( _("teeth"), str(T33), "teeth", "Tooth"),
            T34: ( _("teeth"), str(T34), "teeth", "Tooth"),
            T35: ( _("teeth"), str(T35), "teeth", "Tooth"),
            T36: ( _("teeth"), str(T36), "teeth", "Tooth"),
            T37: ( _("teeth"), str(T37), "teeth", "Tooth"),
            T38: ( _("teeth"), str(T38), "teeth", "Tooth"),
            T41: ( _("teeth"), str(T41), "teeth", "Tooth"),
            T42: ( _("teeth"), str(T42), "teeth", "Tooth"),
            T43: ( _("teeth"), str(T43), "teeth", "Tooth"),
            T44: ( _("teeth"), str(T44), "teeth", "Tooth"),
            T45: ( _("teeth"), str(T45), "teeth", "Tooth"),
            T46: ( _("teeth"), str(T46), "teeth", "Tooth"),
            T47: ( _("teeth"), str(T47), "teeth", "Tooth"),
            T48: ( _("teeth"), str(T48), "teeth", "Tooth"),
            T51: ( _("teeth"), str(T51), "teeth", "Tooth"),
            T52: ( _("teeth"), str(T52), "teeth", "Tooth"),
            T53: ( _("teeth"), str(T53), "teeth", "Tooth"),
            T54: ( _("teeth"), str(T54), "teeth", "Tooth"),
            T55: ( _("teeth"), str(T55), "teeth", "Tooth"),
            T61: ( _("teeth"), str(T61), "teeth", "Tooth"),
            T62: ( _("teeth"), str(T62), "teeth", "Tooth"),
            T63: ( _("teeth"), str(T63), "teeth", "Tooth"),
            T64: ( _("teeth"), str(T64), "teeth", "Tooth"),
            T65: ( _("teeth"), str(T65), "teeth", "Tooth"),
            T71: ( _("teeth"), str(T71), "teeth", "Tooth"),
            T72: ( _("teeth"), str(T72), "teeth", "Tooth"),
            T73: ( _("teeth"), str(T73), "teeth", "Tooth"),
            T74: ( _("teeth"), str(T74), "teeth", "Tooth"),
            T75: ( _("teeth"), str(T75), "teeth", "Tooth"),
            T81: ( _("teeth"), str(T81), "teeth", "Tooth"),
            T82: ( _("teeth"), str(T82), "teeth", "Tooth"),
            T83: ( _("teeth"), str(T83), "teeth", "Tooth"),
            T84: ( _("teeth"), str(T84), "teeth", "Tooth"),
            T85: ( _("teeth"), str(T85), "teeth", "Tooth"),
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

CROWN_SIDE_ALL = 0
CROWN_SIDE_OCCLUSAL = 1
CROWN_SIDE_BUCCAL = 2
CROWN_SIDE_LINGUAL = 3
CROWN_SIDE_MESIAL = 4
CROWN_SIDE_DISTAL = 5

CROWN_SIDES = {
            CROWN_SIDE_ALL: ( _("all"), ),
            CROWN_SIDE_OCCLUSAL: ( _("occlusal"), ),
            CROWN_SIDE_BUCCAL: ( _("buccal"), ),
            CROWN_SIDE_LINGUAL: ( _("lingual"), ),
            CROWN_SIDE_MESIAL: ( _("mesial"), ),
            CROWN_SIDE_DISTAL: ( _("distal"), ),
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

ROOT_CANAL_ALL = 0
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
            ROOT_CANAL_ALL: ( _("all"), ),
            ROOT_CANAL_CENTRAL: ( _("central"), ),
            ROOT_CANAL_BUCCAL: ( _("buccal"), ),
            ROOT_CANAL_LINGUAL: ( _("lingual"), ),
            ROOT_CANAL_MESIAL: ( _("mesial"), ),
            ROOT_CANAL_DISTAL: ( _("distal"), ),
            ROOT_CANAL_MESIO_BUCCAL: ( _("mesio-buccal"), ),
            ROOT_CANAL_MESIO_LINGUAL: ( _("mesio-lingual"), ),
            ROOT_CANAL_DISTO_BUCCAL: ( _("disto-buccal"), ),
            ROOT_CANAL_DISTO_LINGUAL: ( _("disto-lingual"), ),
            ROOT_CANAL_MESIO_BUCCAL_2: ( _("mesio-buccal 2"), ),
            }

PERIODONTE_STATE_SANE = 0
PERIODONTE_STATE_GINGIVITIS = 1
PERIODONTE_STATE_PARODONTITIS = 2

PERIODONTE_STATES = {
            PERIODONTE_STATE_SANE: ( _('sane'), ),
            PERIODONTE_STATE_GINGIVITIS: ( _('gingivitis'), ),
            PERIODONTE_STATE_PARODONTITIS: ( _('parodontitis') ),
            }

PERIODONTAL_LOC_MESIO_BUCCAL = 1
PERIODONTAL_LOC_BUCCAL = 2
PERIODONTAL_LOC_DISTO_BUCCAL = 3
PERIODONTAL_LOC_DISTO_LINGUAL = 4
PERIODONTAL_LOC_LINGUAL = 5
PERIODONTAL_LOC_MESIO_LINGUAL = 6

PERIODONTAL_LOCATIONS = {
            PERIODONTAL_LOC_MESIO_BUCCAL: _('mesio buccal'),
            PERIODONTAL_LOC_BUCCAL: _('buccal'),
            PERIODONTAL_LOC_DISTO_BUCCAL: _('disto buccal'),
            PERIODONTAL_LOC_DISTO_LINGUAL: _('disto lingual'),
            PERIODONTAL_LOC_LINGUAL: _('lingual'),
            PERIODONTAL_LOC_MESIO_LINGUAL: _('mesio lingual'),
            }


TOOTH_EVENT_LOCATION_TOOTH = 0
TOOTH_EVENT_LOCATION_CROWN = 1
TOOTH_EVENT_LOCATION_ROOT = 2
TOOTH_EVENT_LOCATION_PERIODONTE = 3

TOOTH_EVENT_LOCATIONS = {
            TOOTH_EVENT_LOCATION_TOOTH: _("tooth"),
            TOOTH_EVENT_LOCATION_CROWN: _("crown"),
            TOOTH_EVENT_LOCATION_ROOT: _("root"),
            TOOTH_EVENT_LOCATION_PERIODONTE: _("periodonte"),
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
            UNITY_PIECE: ( _("pieces/items"), 'UNITY_PIECE' ), 
            UNITY_VOLUME: ( _("volume in mL"), 'UNITY_VOLUME' ), 
            UNITY_WEIGHT: ( _("weight in gr"), 'UNITY_WEIGHT' ), 
            UNITY_LENGTH: ( _('length in m'), 'UNITY_LENGTH' ),
        }

