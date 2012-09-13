#!/bin/bash --rcfile ~/.bashodontuxrc

cotid=$(odontux add_cotationfr -k 1 -m 1) 
odontux add_acttype -n "Consultation" --cotation $cotid
cotid=$(odontux add_cotationfr -k 1 -m 0)
odontux add_acttype -n "Consultation gratuite" -a "Consultation free, offerte" --cotation $cotid
cotid=$(odontux add_cotationfr -k 1 -m 1 --exceeding_adult_normal 4 --exceeding_adult_cmu 4)
odontux add_acttype -n "Bilan Bucco Dentaire" -a "BBD" -s 9 --cotation $cotid
cotid=$(odontux add_cotationfr -k 1 -m 1 --exceeding_adult_normal 15 --exceeding_adult_cmu 15)
odontux add_acttype -n "Bilan Bucco Dentaire 1 ou 2 radios" -a "BBD 1-2 radio" -s 9 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 7 --kid_multiplicator 8)
odontux add_acttype -n "Obturation coronaire 1 face, technique directe" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 1 face, technique directe" -a "Amalgame 1 face" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 1 face, technique directe" -a "Composite 1 face" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 1 face, technique directe" -a "CVI 1 face" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 12 --kid_multiplicator 14)
odontux add_acttype -n "Obturation coronaire 2 faces, technique directe" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 2 faces, technique directe" -a "Amalgame 2 faces" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 2 faces, technique directe" -a "Composite 2 faces" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 2 faces, technique directe" -a "CVI 2 faces" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 17 --kid_multiplicator 20) 
odontux add_acttype -n "Obturation coronaire 3 faces, technique directe" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 3 faces, technique directe" -a "Amalgame 3 faces " -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 3 faces, technique directe" -a "Composite 3 faces " -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire 3 faces, technique directe" -a "CVI 3 faces" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 33)
odontux add_acttype -n "Obturation coronaire d'au moins 2 faces par insertion d'un matériau en phase plastique avec ancrage radiculaire" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire d'au moins 2 faces par insertion d'un matériau en phase plastique avec ancrage radiculaire" -a "RCR amalgame" -s 3 --cotation $cotid
odontux add_acttype -n "Obturation coronaire d'au moins 2 faces par insertion d'un matériau en phase plastique avec ancrage radiculaire" -a "RCR composite" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 17 --exceeding_adult_normal 179.03)
odontux add_acttype -n "Obturation coronaire, 3 faces par une technique indirecte de laboratoire en métal" -a "inlay 3 faces métal" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 17 --exceeding_adult_normal 303.03)
odontux add_acttype -n "Obturation coronaire, 3 faces par une technique indirecte de laboratoire en céramique" -a "Inlay 3 faces ceramique" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 9)
odontux add_acttype -n "Scellement prophylactique des puits, sillons et fissures, par dent (valable avant 14 ans, sur les x6 et x7)" -a "Sealant" -s 3 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 7 --kid_multiplicator 10)
odontux add_acttype -n "Pulpotomie, pulpectomie coronaire, avec obturation de la chambre pulpaire" -s 4 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 14 --kid_multiplicator 16)
odontux add_acttype -n "Pulpectomie coronaire et radiculaire, groupe incisivo-canin" -s 4 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 20 --kid_multiplicator 24)
odontux add_acttype -n "Pulpectomie coronaire et radiculaire, groupe prémolaires" -s 4 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 34 --kid_multiplicator 39)
odontux add_acttype -n "Pulpectomie coronaire et radiculaire, groupe molaires" -s 4 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 12)
odontux add_acttype -n "Détartrage" -a "Detartrage" -s 2 --cotation $cotid
odontux add_acttype -n "Détartrage 2nde séance" -s 2 --cotation $cotid
cotid=$(odontux add_cotationfr -k 10 -m 0 --exceeding_adult_normal 27)
odontux add_acttype -n "Aero Polissage" -a "Polissage" -s 2 --cotation $cotid
cotid=$(odontux add_cotationfr -k 10 -m 0 --exceeding_adult_normal 500)
odontux add_acttype -n "blanchiment, blanchiement, blanchissement, éclaircissement" -a "eclaircissement" -s 10 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 8)
odontux add_acttype -n "Ligature métallique dans les parodontopathies" -s 2 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 40)
odontux add_acttype -n "Attelle métallique dans les parodontopathies" -s 2 --cotation $cotid
cotid=$(odontux add_cotationfr -k 3 -m 70)
odontux add_acttype -n "Prothèse attelle de contention quelque soit le nombre de dents ou de crochets" -s 2 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 20)
odontux add_acttype -n "Gingivectomie étendue à un sextant" -s 2 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 20)
odontux add_acttype -n "Gingivectomie étendue à un sextant" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 16)
odontux add_acttype -n "Extraction d'une dent permanente" -a "Avulsion dent définitive" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 8)
odontux add_acttype -n "Extraction de chacune des dents permanentes suivantes, dans la même séance" -a "Avulsion dents suivantes" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 8)
odontux add_acttype -n "Extraction d'une dent déciduale, quelque soit la technique" -a "Avulsion dent lactéale" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 4)
odontux add_acttype -n "Extraction de chacune des dents déciduales suivantes, dans la même séance" -a "Avulsion lactéales suivantes" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 10)
odontux add_acttype -n "Extraction d'une dent par alvéolectomie" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 40)
odontux add_acttype -n "Extraction d'une dent de sagesse incluse, enclavée ou état de germe" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 20)
odontux add_acttype -n "Extraction des dents de sagesse incluses, enclavées ou état de germe suivantes, même séance" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 20)
odontux add_acttype -n "Germectomie pour une autre dent que la dent de sagesse" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 40)
odontux add_acttype -n "Extraction d'une dent incluse ou enclavée" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 50)
odontux add_acttype -n "Extraction d'une canine incluse" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 40)
odontux add_acttype -n "Extraction d'une odontoïde, ou dent surnuméraire incluse ou enclavée" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 20)
odontux add_acttype -n "Extraction d'une dent en désinclusion non enclavée, dont la couronne est sous-muqueuse" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 50)
odontux add_acttype -n "Extraction d'une dent en désinclusion, dont la couronne est sous-muqueuse en position palatine ou linguale" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 80)
odontux add_acttype -n "Extraction d'une dent ectopique et incluse (coroné, gonion, ramus, bord basilaire, sinus" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 100)
odontux add_acttype -n "Extraction chirurgicale dent permanente incluse, traitement radiculaire éventuel, réimplantation et contention" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 150)
odontux add_acttype -n "Extraction chirurgicale de 2 dents permanentes incluses, traitement radiculaire éventuel, réimplantation et contention" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 40)
odontux add_acttype -n "Trépanation du sinus maxillaire, par voie vestibulaire, pour recherche racine dentaire" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 5)
odontux add_acttype -n "Dégagement chirurgical de la couronne d'une dent permanente incluse" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 30)
odontux add_acttype -n "Régularisation d'une crête alvéolaire avec suture gingivale localisée, autre séance que celle de l'extraction" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 15)
odontux add_acttype -n "Régularisation d'une crête alvéolaire avec suture gingivale étendue à crête d'un hémimaxillaire, ou canine-canine" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 30)
odontux add_acttype -n "Régularisation d'une crête alvéolaire avec suture gingivale étendue à la totalité de la crête" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 24)
odontux add_acttype -n "Curetage périapical, avec ou sans résection apicale (radio obligatoire, TTT et obturation canalaire non compris" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 24)
odontux add_acttype -n "Curetage périapical, avec ou sans résection apicale (radio obligatoire, TTT et obturation canalaire non compris" -s 4 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 15)
odontux add_acttype -n "Exérèse chirurgicale d'un kyste : petit volume, voie alvéolaire élargie" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 30)
odontux add_acttype -n "Exérèse chirurgicale d'un kyste : étendu aux apex de 2 dents, nécessitant trépanation osseuse" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 2 -m 50)
odontux add_acttype -n "Exérèse chirurgicale d'un kyste : étendu à un segment important du maxillaire" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 6 -m 10)
odontux add_acttype -n "Traitement d'une hémorragie post-opératoire dans une séance autre que celle de l'intervention" -s 5 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 3 -m 50 --adult_cmu_num 1 --exceeding_adult_normal 147.5 --exceeding_adult_cmu 122.5)
odontux add_acttype -n "Couronne dentaire faisant intervenir une technique de coulée métallique" -a "CCA, couronne coulée métallique" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 3 -m 50 --adult_cmu_num 3 --exceeding_adult_normal 342.5 --exceeding_adult_cmu 267.5)
odontux add_acttype -n "Couronne dentaire faisant intervenir une technique de coulée métallique" -a "CCMonocouche, Couronne Céramo Métallique Monocouche" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 3 -m 50 --adult_cmu_num 3 --exceeding_adult_normal 447.5 --exceeding_adult_cmu 267.5)
odontux add_acttype -n "Couronne dentaire faisant intervenir une technique de coulée métallique" -a "CCM, Couronne Céramo Métallique Multicouches" -s 6 --cotation $cotid
odontux add_acttype -n "Couronne dentaire faisant intervenir une technique de coulée métallique" -a "CCC, Couronne Céramo Céramique" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 3 -m 30 --adult_cmu_num 42 --exceeding_adult_normal 455.5 --exceeding_adult_cmu 128.5)
odontux add_acttype -n "Inter de brigde en céramique" -a "Inter CCM ceramique" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 57 --exceeding_adult_normal 47.45)
odontux add_acttype -n "Conception, adaptation et pose d'une infrastructure corono-radiculaire métallique coulée à ancrage radiculaire (inlay-core)" -a "Inlay Core" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 67 --exceeding_adult_normal 45.95)
odontux add_acttype -n "Conception, adaptation et pose d'un inlay-core à clavette" -a "Inlay Core à clavette" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 3 -m 35 --adult_cmu_num 4 --exceeding_adult_cmu 0)
odontux add_acttype -n "Dent à tenon, dans groupe incisivo-canin-prémolaire" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 10 -m 0 --exceeding_adult_normal 35 --exceeding_adult_cmu 0)
odontux add_acttype -n "Dépose de prothèse conjointes métalliques" -a "Dépose couronne" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 18)
odontux add_acttype -n "Dépose de prothèses conjointes métalliques, pour TTT radiothérapique de tumeurs faciales, obturation provisoire comprise, par élément pilier" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 10 -m 0 --exceeding_adult_normal 28 --exceeding_kid_normal 28 --exceeding_adult_cmu 0)
odontux add_acttype -n "Rescellement des travaux de prothèse conjointe, par élément" -a "rescellement, chaque element" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 1 -m 30 --adult_cmu_num 6 --exceeding_adult_cmu 128.5)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 1 à 3 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 1 à 3 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 35 --keycmu 1 --adult_cmu_num 7 --exceeding_adult_cmu 273.75)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 4 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 4 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 40 --keycmu 1 --adult_cmu_num 8 --exceeding_adult_cmu 263.00)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 5 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 5 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 45 --keycmu 1 --adult_cmu_num 9 --exceeding_adult_cmu 252.25)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 6 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 6 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 50 --keycmu 1 --adult_cmu_num 10 --exceeding_adult_normal 742.5 --exceeding_adult_cmu 326.50)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 7 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 7 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 55 --keycmu 1 --adult_cmu_num 11 --exceeding_adult_cmu 315.75)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 8 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 8 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 60 --keycmu 1 --adult_cmu_num 12 --exceeding_adult_cmu 305.00)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 9 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 9 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 65 --keycmu 1 --adult_cmu_num 13 --exceeding_adult_cmu 294.25)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 10 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 10 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 70 --keycmu 1 --adult_cmu_num 14 --exceeding_adult_cmu 366.50)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 11 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 11 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 75 --keycmu 1 --adult_cmu_num 15 --exceeding_adult_cmu 355.75)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 12 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 12 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 80 --keycmu 1 --adult_cmu_num 16 --exceeding_adult_cmu 345.00)
odontux add_acttype -n "Prothèse amovible partielle adjointe résine maxillaire, de 13 dents" -a "PAP resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe résine mandibulaire, de 13 dents" -a "PAP resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 85 --keycmu 1 --adult_cmu_num 17 --exceeding_adult_normal 1342.25 --exceeding_adult_cmu 473.25)
odontux add_acttype -n "Prothèse amovible totale maxillaire résine" -a "PAT maxillaire resine" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible totale mandibulaire résine" -a "PAT maxillaire resine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 --keycmu 1 -m 90 --adult_cmu_num 6 --exceeding_adult_cmu 128.5)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 1 à 3 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 1 à 3 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 95 --keycmu 1 --adult_cmu_num 7 --exceeding_adult_normal 1125 --exceeding_adult_cmu 273.75)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 4 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 4 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 100 --keycmu 1 --adult_cmu_num 8 --exceeding_adult_normal 1045.75 --exceeding_adult_cmu 263.00)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 5 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 5 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 105 --keycmu 1 --adult_cmu_num 9 --exceeding_adult_cmu 252.25)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 6 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 6 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 110 --keycmu 1 --adult_cmu_num 10 --exceeding_adult_normal 742.5 --exceeding_adult_cmu 326.50)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 7 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 7 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 115 --keycmu 1 --adult_cmu_num 11 --exceeding_adult_cmu 315.75)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 8 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 8 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 120 --keycmu 1 --adult_cmu_num 12 --exceeding_adult_cmu 305.00)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 9 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 9 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 125 --keycmu 1 --adult_cmu_num 13 --exceeding_adult_cmu 294.25)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 10 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 10 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 130 --keycmu 1 --adult_cmu_num 14 --exceeding_adult_cmu 366.50)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 11 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 11 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 135 --keycmu 1 --adult_cmu_num 15 --exceeding_adult_cmu 355.75)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 12 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 12 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 140 --keycmu 1 --adult_cmu_num 16 --exceeding_adult_cmu 345.00)
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique maxillaire, de 13 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible partielle adjointe métallique mandibulaire, de 13 dents" -a "PAP metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 145 --keycmu 1 --adult_cmu_num 17 --exceeding_adult_normal 1342.25 --exceeding_adult_cmu 473.25)
odontux add_acttype -n "Prothèse amovible totale métallique maxillaire" -a "PAT metal stellite" -s 6 --cotation $cotid
odontux add_acttype -n "Prothèse amovible totale métallique mandibulaire" -a "PAT metal stellite" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 60 --keycmu 1 --adult_cmu_num 22 --exceeding_adult_cmu 171.00)
odontux add_acttype -n "Plaque base métallique, supplément" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 10 --keycmu 2 --adult_cmu_num 20 --exceeding_adult_normal 93.5 --exceeding_adult_cmu 43.5)
odontux add_acttype -n "Dents ajoutée ou remplacée sur appareils matière plastique, 1er élément" -a "1 dent ajoutee sur PAP" -s 6 --cotation $cotid
odontux add_acttype -n "Crochet ajouté ou remplacé sur appareils matière plastique, 1er élément" -a "1 crochet ajoute sur PAP" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 5 --keycmu 2 --adult_cmu_num 21 --exceeding_adult_normal 59.25 --exceeding_adult_cmu 21.75)
odontux add_acttype -n "Dents ajoutée ou remplacée sur appareils matière plastique, éléments suivants" -a "dents suivantes ajoutees sur PAP" -s 6 --cotation $cotid
odontux add_acttype -n "Crochets ajoutée ou remplacée sur appareils matière plastique, éléments suivants" -a "crochets suivants ajoutes sur PAP" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 15 --keycmu 2 --adult_cmu_num 25 --exceeding_adult_normal 93.5 --exceeding_adult_cmu 32.75)
odontux add_acttype -n "Réparation de fracture de la plaque base métallique" -a "Reparation fracture stellite metallique" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 4 -m 10 --keycmu 2 --adult_cmu_num 19 --exceeding_adult_normal 93.5 --exceeding_adult_cmu 43.5)
odontux add_acttype -n "Réparation de fracture de la plaque base résine" -a "Reparation fracture résine" -s 6 --cotation $cotid
cotid=$(odontux add_cotationfr -k 5 -m 6)
odontux add_acttype -n "Radio retro-alvéolaire, RVG" -s 8 --cotation $cotid
cotid=$(odontux add_cotationfr -k 5 -m 21)
odontux add_acttype -n "Radiographie panoramique dentaire, orthopantomogramme" -s 8 --cotation $cotid
