# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/25
# v0.4
# Licence BSD
#

from log import (index, login, logout)
from administration import (
                 allpatients,
                 enter_patient_file,
                 add_patient,
                 update_patient,
                 update_patient_address, add_patient_address, 
                 delete_patient_address,
                 update_patient_phone, add_patient_phone, delete_patient_phone,
                 update_patient_mail, add_patient_mail, delete_patient_mail,
                 )
from search import find
from act import (list_gesture, add_gesture, update_gesture, view_gesture,
                 list_specialty, add_specialty, update_specialty)
from md import (
                list_md,
                add_md,
                update_md,
                update_md_address, add_md_address, delete_md_address,
                update_md_phone, add_md_phone, delete_md_phone,
                update_md_mail, add_md_mail, delete_md_mail,
                )
from users import (
                list_users,
                add_user,
                update_user,
                update_user_address, add_user_address, delete_user_address,
                update_user_phone, add_user_phone, delete_user_phone,
                update_user_mail, add_user_mail, delete_user_mail,
                )
from anamnesis import (
                add_anamnesis_entry,
                portal_anamnesis,
                add_survey, add_question, list_survey, list_question,
                view_survey, view_question, add_question_to_survey,
                remove_question_from_survey, update_survey_name,
                update_question, delete_survey
                    )
from medication import (
                    list_drugs,
                    update_drug, delete_drug, add_drug,
                    choose_drugs_to_prescribe
                    )
from schedule import (
                    agenda_date,
                    agenda,
                    display_day,
                    add_appointment,
                    )
from patient import (
                    enter_patient_appointment,
                    )
from teeth import (
                    list_teeth
                  )
from assets import (
                    my_assets, add_provider, list_providers, list_assets, 
                    add_asset, add_kit_type
                    )
from traceability import (
                    traceability_portal, add_sterilization_cycle_type,
                    list_sterilization_cycle_type,
                    update_sterilization_cycle_type,
                    add_sterilization_complement, 
                    list_sterilization_complement,
                    update_sterilization_complement,
                    add_sterilization_cycle_mode,
                    list_sterilization_cycle_mode,
                    update_sterilization_cycle_mode
                    )
from event import (
                choose_event_location
                    )
