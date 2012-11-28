# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/25
# v0.4
# Licence BSD
#

from actions import (add_generic, update_generic, list_generic)
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
from act import (list_acttype, add_acttype, update_acttype,
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
from cotation import (
                     show_ngap 
                     )
from anamnesis import (
                    list_anamnesis,
                    update_medical_history, delete_medical_history, 
                    add_medical_history,
                    update_past_surgery, delete_past_surgery,
                    add_past_surgery,
                    update_allergies, delete_allergies, add_allergies
                    )
from medication import (
                    list_drugs,
                    update_drug, delete_drug, add_drug,
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
