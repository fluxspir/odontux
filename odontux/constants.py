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

