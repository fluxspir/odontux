#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

from gettext import gettext as _

LOCALE = "fr"

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

END_USE_REASON = [ (0, _('In stock or in use') ), ( 1, _('Natural end of the asset')),
            (2, _('Unconvenient') ), (3, _('Obsolete / Out of date') ), 
            (4, _('Remove from market') ), (5, _('Lost') ) ]

