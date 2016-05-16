#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

from gettext import gettext as _
import ConfigParser
import os

parser = ConfigParser.ConfigParser()
home = os.path.expanduser("~")
parser.read(os.path.join(home, ".odontuxrc"))
LOCALE = parser.get("environment", "locale").title()

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
MAXILAR = 1
MANDIBULAR = 2
QUADRANT_SUPERIOR_RIGHT = 10
QUADRANT_SUPERIOR_LEFT = 20
QUADRANT_INFERIOR_LEFT = 30
QUADRANT_INFERIOR_RIGHT = 40
SEXTANT_SUPERIOR_RIGHT = 3
SEXTANT_SUPERIOR_CENTRAL = 4
SEXTANT_SUPERIOR_LEFT = 5
SEXTANT_INFERIOR_LEFT = 6
SEXTANT_INFERIOR_CENTRAL = 7
SEXTANT_INFERIOR_RIGHT = 8

TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_DEFINITIVE = 11
TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_DEFINITIVE = 12
TOOTH_CANINA_SUPERIOR_RIGHT_DEFINITIVE = 13
TOOTH_FIRST_PREMOLAR_SUPERIOR_RIGHT_DEFINITIVE = 14
TOOTH_SECOND_PREMOLAL_SUPERIOR_RIGHT_DEFINITIVE = 15
TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_DEFINITIVE = 16
TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_DEFINITIVE = 17
TOOTH_THIRD_MOLAR_SUPERIOR_RIGHT_DEFINITIVE = 18
TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_DEFINITIVE = 21
TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_DEFINITIVE = 22
TOOTH_CANINA_SUPERIOR_LEFT_DEFINITIVE = 23
TOOTH_FIRST_PREMOLAR_SUPERIOR_LEFT_DEFINITIVE = 24
TOOTH_SECOND_PREMOLAL_SUPERIOR_LEFT_DEFINITIVE = 25
TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_DEFINITIVE = 26
TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_DEFINITIVE = 27
TOOTH_THIRD_MOLAR_SUPERIOR_LEFT_DEFINITIVE = 28
TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_DEFINITIVE = 31
TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_DEFINITIVE = 32
TOOTH_CANINA_INFERIOR_LEFT_DEFINITIVE = 33
TOOTH_FIRST_PREMOLAR_INFERIOR_LEFT_DEFINITIVE = 34
TOOTH_SECOND_PREMOLAL_INFERIOR_LEFT_DEFINITIVE = 35
TOOTH_FIRST_MOLAR_INFERIOR_LEFT_DEFINITIVE = 36
TOOTH_SECOND_MOLAR_INFERIOR_LEFT_DEFINITIVE = 37
TOOTH_THIRD_MOLAR_INFERIOR_LEFT_DEFINITIVE = 38
TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_DEFINITIVE = 41
TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_DEFINITIVE = 42
TOOTH_CANINA_INFERIOR_RIGHT_DEFINITIVE = 43
TOOTH_FIRST_PREMOLAR_INFERIOR_RIGHT_DEFINITIVE = 44
TOOTH_SECOND_PREMOLAL_INFERIOR_RIGHT_DEFINITIVE = 45
TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_DEFINITIVE = 46
TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_DEFINITIVE = 47
TOOTH_THIRD_MOLAR_INFERIOR_RIGHT_DEFINITIVE = 48
DEFINITIVE_SUPERIOR_TEETH_POSITIONS = ( 
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
DEFINITIVE_INFERIOR_TEETH_POSITIONS = (
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

TOOTH_INCISIVO_CENTRAL_SUPERIOR_RIGHT_TEMPORARY = 51
TOOTH_INCISIVO_LATERAL_SUPERIOR_RIGHT_TEMPORARY = 52
TOOTH_CANINA_SUPERIOR_RIGHT_TEMPORARY = 53
TOOTH_FIRST_MOLAR_SUPERIOR_RIGHT_TEMPORARY = 54
TOOTH_SECOND_MOLAR_SUPERIOR_RIGHT_TEMPORARY = 55
TOOTH_INCISIVO_CENTRAL_SUPERIOR_LEFT_TEMPORARY = 61
TOOTH_INCISIVO_LATERAL_SUPERIOR_LEFT_TEMPORARY = 62
TOOTH_CANINA_SUPERIOR_LEFT_TEMPORARY = 63
TOOTH_FIRST_MOLAR_SUPERIOR_LEFT_TEMPORARY = 64
TOOTH_SECOND_MOLAR_SUPERIOR_LEFT_TEMPORARY = 65
TOOTH_INCISIVO_CENTRAL_INFERIOR_LEFT_TEMPORARY = 71
TOOTH_INCISIVO_LATERAL_INFERIOR_LEFT_TEMPORARY = 72
TOOTH_CANINA_INFERIOR_LEFT_TEMPORARY = 73
TOOTH_FIRST_MOLAR_INFERIOR_LEFT_TEMPORARY = 74
TOOTH_SECOND_MOLAR_INFERIOR_LEFT_TEMPORARY = 75
TOOTH_INCISIVO_CENTRAL_INFERIOR_RIGHT_TEMPORARY = 81
TOOTH_INCISIVO_LATERAL_INFERIOR_RIGHT_TEMPORARY = 82
TOOTH_CANINA_INFERIOR_RIGHT_TEMPORARY = 83
TOOTH_FIRST_MOLAR_INFERIOR_RIGHT_TEMPORARY = 84
TOOTH_SECOND_MOLAR_INFERIOR_RIGHT_TEMPORARY = 85



ANATOMIC_LOCATION = {
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

###############
## teeth events
##
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

#TOOTH_EVENT_ATTRIBUTES = [ "sane", "place", "mobility", "fracture", "absence",
#                           "replaced", "implant" ]
#CROWN_EVENT_ATTRIBUTES = [ "sealing", "decay", "obturation", "crowned", 
#                           "bridge" ]
#ROOT_EVENT_ATTRIBUTES = [ "infected", "abscess", "obturation", "inlaycore" ]

END_USE_REASON_IN_USE_STOCK = 0
END_USE_REASON_NATURAL_END = 1
END_USE_REASON_UNCONVENIENT = 2
END_USE_REASON_OBSOLETE = 3
END_USE_REASON_REMOVE_MARKET = 4
END_USE_REASON_LOST = 5
END_USE_REASON = [ (END_USE_REASON_IN_USE_STOCK, _('In stock or in use') ), 
                ( END_USE_REASON_NATURAL_END, _('Natural end of the asset')),
                ( END_USE_REASON_UNCONVENIENT, _('Unconvenient') ), 
                ( END_USE_REASON_OBSOLETE, _('Obsolete / Out of date') ), 
                ( END_USE_REASON_REMOVE_MARKET, _('Remove from market') ), 
                ( END_USE_REASON_LOST, _('Lost') ) 
                ]

UNITY_PIECE = 0
UNITY_VOLUME = 1
UNITY_WEIGHT = 2
UNITY_LENGTH = 3
UNITY = [ ( UNITY_PIECE, _("pieces/items") ), 
            ( UNITY_VOLUME, _("volume in mL") ), 
            ( UNITY_WEIGHT, _("weight in gr") ), 
            ( UNITY_LENGTH, _('length in m') ) 
        ]

