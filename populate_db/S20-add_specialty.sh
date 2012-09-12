#!/bin/bash --rcfile ~/.bashodontuxrc

specialties="diagnostic periodontic operative_dentistry endodontic chirurgia prosthetic orthodontic radiology pedodontic esthetic"

for s in $specialties ; do
    odontux add_specialty -n $s; 
done    

