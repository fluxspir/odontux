#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

from gettext import gettext as _

ROLE_DENTIST = 0
ROLE_NURSE = 1
ROLE_ASSISTANT = 2
ROLE_SECRETARY = 3
ROLE_ADMIN = 4

ROLES = { ROLE_DENTIST: _("dentist"),
          ROLE_NURSE: _("nurse"),
          ROLE_ASSISTANT: _("assistant"),
          ROLE_SECRETARY: _("secretary"),
          ROLE_ADMIN: _("admin"),
        }

#ROLES_LIST = [(k, ROLES[k]) for k in ROLES.keys()]
ROLES_LIST = ROLES.items()

KID_AGE = 13
