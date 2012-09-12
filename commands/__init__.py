# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/25
# v0.4
# Licence BSD

from specialty import AddSpecialtyCommand, ListSpecialtyCommand
from users import (AddOdontuxUserCommand, AddDentalOfficeCommand,
                   UserMovingInCommand)
from md import (AddMedecineDoctorCommand, ListMedecineDoctorCommand,
                UpdateMedecineDoctorCommand)
from cotation import (AddNgapKeyFrCommand, AddCmuKeyFrCommand,
                      AddMajorationFrCommand, AddCotationFrCommand,
                      ListNgapKeyFrCommand, ListCmuKeyFrCommand,
                      ListCotationFrCommand, UpdateCotationFrCommand)
from administration import (AddPatientCommand, ListPatientCommand,
                            UpdatePatientCommand)
from act import (AddActTypeCommand, AddAdministrativeActCommand,
                 ListActTypeCommand, ListPatientActCommand)
from anamnesis import (AddMedicalHistoryCommand, AddPastSurgeriesCommand,
                       AddAllergiesCommand, ListMedicalHistoryCommand,
                       ListSurgeriesCommand, ListAllergiesCommand,
                       UpdateMedicalHistoryCommand, UpdatePastSurgeriesCommand,
                       UpdateAllergiesCommand)
from schedule import (AddAppointmentCommand, AddAppointmentMemoCommand,
                      ListAppointmentCommand, ListAppointmentMemoCommand,
                      UpdateAppointmentCommand)
from teeth import (AddToothEventCommand, GetToothIdCommand, 
                   AddCrownEventCommand, AddRootEventCommand, 
                   ListPatientTeethCommand)
from medication import (AddDrugPrescribedCommand, MakePrescriptionCommand, 
                        ListDrugCommand)
