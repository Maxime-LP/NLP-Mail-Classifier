# -*- coding: utf-8 -*-           
import os         
import win32com.client        
from collections import defaultdict
import csv

def killer():
    try:
        os.system('taskkill /f /im OUTLOOK.exe >nul 2>&1')       
    except:
        pass
#https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.mailitem?redirectedfrom=MSDN&view=outlook-pia#properties_
def ReadMail(message,directory):   
    print(message.Subject)
    mail = defaultdict(str)
    if directory == 'Assistance' and message.Subject.lower()[:3] != 're:' and message.Subject.lower()[:4] != 're :':
        mail['demande_de_support'] = '1'
    elif directory == 'Non assistance':
        mail['demande_de_support'] = '0'
    elif message.SenderName.lower() in ['chable brice','plonquet nadège','courtais yohan','le paumier maxime']:
        mail['demande_de_support'] = '0'
    elif message.Subject.lower()[:3] == 're:' or message.Subject.lower()[:4] == 're :':
        mail['demande_de_support'] = '0'
    else:
        mail['demande_de_support'] = 'unkown'
    
    mail['sender'] = str(message.SenderName.lower())
    mail['date'] = str(message.LastModificationTime)
    #mail['rec'] = str(message.To.lower() + message.CC.lower() + message.BCC.lower())
    mail['object'] = str(message.Subject.lower())
    mail['attached_files'] = str(message.Attachments.Count)
    mail['body'] = str(message.Body.lower().replace('\r\n\r\n',' ').replace('\r','').replace('\n',''))
    
    return mail

def Parser(path):
    #Les fichiers doivent se trouver dans deux sous dossiers
    # en fonction de leur label
    killer()
    list_of_mails = []
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    mails_dropped = []
    for root,dirs,files in os.walk(path):
        for file in files:
            try:
                directory = root.split('\\')[11]
                message = outlook.OpenSharedItem(os.path.join(root,file))
                list_of_mails.append(ReadMail(message,directory))
            except:
                print("Erreur : mail ignoré")
                mails_dropped.append(file)
    print(len(mails_dropped),'mails ignorés :',mails_dropped)
    return list_of_mails

def write_csv(path):
    #path variable is the path to the mail folders
    
    list_of_mails = Parser(path)
    with open('mails.csv','w',encoding='utf-16') as csvfile:
        spamwriter = csv.writer(csvfile,delimiter='¤',quotechar="§")
        spamwriter.writerow(['demande_de_support','sender','date','object','attached_files','body'])
        spamwriter.writerows([mail.values() for mail in list_of_mails])

if __name__=='__main__':
    path = r'\\HM.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail'
    write_csv(path)