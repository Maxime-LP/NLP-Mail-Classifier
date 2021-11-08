# -*- coding: utf-8 -*-           
import os, re, csv        
import win32com.client        
from collections import defaultdict

def outlookKiller():
    try:
        os.system('taskkill /f /im OUTLOOK.exe >nul 2>&1')       
    except:
        pass

#https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.mailitem?redirectedfrom=MSDN&view=outlook-pia#properties_
def ReadMail(message,directory):   
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
    mail['attached_files'] = str(message.Attachments.Count)

    mail['text'] = message.Subject.lower() + ' ' + message.Body.lower()

    #Removes html
    mail['text'] = re.sub("<(mailto|https?).+>","",mail['text'])
    #Removes phone numbers
    mail['text'] = re.sub("([0-9]{2}\s){5}","",mail['text'])
    mail['text'] = re.sub("[0-9]{2}(%20[0-9]{2}){4}","",mail['text'])
    #Removes link markers
    mail['text'] = re.sub("https?|www","",mail['text'])

    #Finds the words of 2 letters or more
    pattern = re.compile(r"\b\w{2,}\b")
    words = pattern.findall(mail['text'])
    mail['text'] = ' '.join(words)

    return mail

def Parser(path):
    #path > Assistance / Non assistance
    outlookKiller()
    mails = []
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    mails_dropped = []
    for root,dirs,files in os.walk(path):
        for file in files:
            try:
                directory = root.split('\\')[-1]
                message = outlook.OpenSharedItem(os.path.join(root,file))
                print(message.Subject)
                mails.append(ReadMail(message,directory))
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print(e," : mail ignoré")
                mails_dropped.append(file)
    print(mails_dropped,len(mails_dropped),'mails ignorés :')
    return mails

def write_csv(path,output='mails.csv'):
    #path variable is the path to the mail folders
    mails = Parser(path)
    with open(output,'w',encoding='utf-16') as csvfile:
        spamwriter = csv.writer(csvfile,delimiter='¤',quotechar="§")
        spamwriter.writerow(['demande_de_support','sender','date','attached_files','text'])
        spamwriter.writerows([mail.values() for mail in mails])

if __name__=='__main__':
    path = r'\\HM.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail'
    output='firstdataset.csv'
    write_csv(path,output)