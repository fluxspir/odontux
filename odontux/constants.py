#!/usr/bin/env python
# Franck Labadille
# 2012/09/02
# v0.4
# Licence BSD

ROLE_DENTIST = 0
ROLE_NURSE = 1
ROLE_ASSISTANT = 2
ROLE_SECRETARY = 3
ROLE_ADMIN = 4

ROLES = { ROLE_DENTIST: "dentist", 
          ROLE_NURSE: "nurse", 
          ROLE_ASSISTANT: "assistant", 
          ROLE_SECRETARY: "secretary", 
          ROLE_ADMIN: "admin",
        }

#ROLES_LIST = [(k, ROLES[k]) for k in ROLES.keys()]
ROLES_LIST = ROLES.items()

KID_AGE = 13
