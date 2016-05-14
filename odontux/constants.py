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


TOOTH_STATES = {
            "s": _("sane"),
            "x": _("sealing"),
            "o": _("obturated"),
            "c": _("crowned"),
            "d": _("decayed"),
            "p": _("placed"),
            "m": _("mobile"),
            "f": _("fracture"),
            "a": _("absent"),
            "b": _("bridge"),
            "r": _("resin"),
            "I": _("implant"),
            "w": _("without_state"),
           }

PERIODONTE_STATES = {
            '0': _('sane'),
            '1': _('gingivitis'),
            '2': _('parodontitis')
            }

EVENT_LOCATION_TOOTH = (0, "tooth")
EVENT_LOCATION_CROWN = (1, "crown")
EVENT_LOCATION_ROOT = (2, "root")

# could be turn to [ ( 0 , "sane" ), (1, "place" ), ...]  after a 
# {models,commands,views}/teeth.py update
TOOTH_EVENT_ATTRIBUTES = [ "sane", "place", "mobility", "fracture", "absence",
                           "replaced", "implant" ]
CROWN_EVENT_ATTRIBUTES = [ "sealing", "decay", "obturation", "crowned", 
                           "bridge" ]
ROOT_EVENT_ATTRIBUTES = [ "infected", "abscess", "obturation", "inlaycore" ]

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

