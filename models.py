# -*- coding: utf-8 -*-

from lemmatization import ImportData

pathhm = '\\HM.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail'
data = ImportData(path=pathhm)
print(data)

X = data.drop(columns=['demande_de_support'])
Y = data['demande_de_support']

types = {0:'Non Assistance', 1:"Assistance"}

#types = {0:'Non Assistance', 1:"Aide à l'utilisation", 2:"Assistance", 3:"Demande d'habilitation", 4:"Demande d'information"}

# extraire direction + service