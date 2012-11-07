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

ROLES_LIST = ROLES.item()

#ROLES_LIST = [ 
#               (ROLES[ROLE_DENTIST], ROLE_DENTIST), 
#               (ROLES[ROLE_NURSE], ROLE_NURSE), 
#               (ROLES[ROLE_ASSISTANT], ROLE_ASSISTANT),
#               (ROLES[ROLE_SECRETARY], ROLE_SECRETARY), 
#               (ROLES[ROLE_ADMIN], ROLE_ADMIN) 
#             ]
#ROLES_LIST = [ 
#              (ROLE_DENTIST,ROLES[ROLE_DENTIST]), 
#              (ROLE_NURSE, ROLES[ROLE_NURSE]), 
#              (ROLE_ASSISTANT, ROLES[ROLE_ASSISTANT]),
#              (ROLE_SECRETARY,ROLES[ROLE_SECRETARY]), 
#              (ROLE_ADMIN, ROLES[ROLE_ADMIN]) 
#            ]

KID_AGE = 13
