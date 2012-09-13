#/bin/bash --rcfile ~/.bashodontuxrc

paid=$(odontux add_patient -t mr -l essai -f papa -s 1 -o 1 -u 1 --street "12 rue lala" --city Paris --postal_code 75015 --county "Ile de France" -b 19700101 --job travail -d $(odontux list_md --id maboule) --date 20120913)
odontux add_medicalhistory --patient $paid -u 1 -d "cholestérol" -t "crestor" --date 20120913
odontux add_surgeries --patient $paid -u 1  --date 20120913
odontux add_allergies --patient $paid -u 1  --date 20120913

faid=$(odontux list_family --id essai papa)
