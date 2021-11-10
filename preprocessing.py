# -*- coding: utf-8 -*-           
import os, re, csv
from pickle import encode_long
import win32com.client        
from collections import defaultdict
import pandas as pd
from lemmatization import lemmatizeDF
from sklearn.feature_extraction.text import HashingVectorizer
tokenizer = HashingVectorizer(strip_accents='unicode').build_tokenizer()

def outlookKiller():
    try:
        os.system('taskkill /f /im OUTLOOK.exe >nul 2>&1')
        os.system('cls')    
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
    mail['text'] = re.sub("([0-9]{2}\s?){5}","",mail['text'])
    mail['text'] = re.sub("[0-9]{2}(%20[0-9]{2}){4}","",mail['text'])
    #Removes link markers
    mail['text'] = re.sub("https?|www","",mail['text'])
    #Finds the words of 2 letters or more
    words = tokenizer(mail['text'])
    mail['text'] = ' '.join(words)
    return mail

def Parser(path):
    #path > Assistance / Non assistance
    outlookKiller()
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    df = pd.DataFrame(data=None,columns=['demande_de_support','sender','date','attached_files','text'])
    mails_dropped = []

    for root,dirs,files in os.walk(path):
        for file in files:
            try:
                directory = root.split('\\')[-1]
                message = outlook.OpenSharedItem(os.path.join(root,file))
                print(message.Subject)
                currentMail = ReadMail(message,directory)
                df = df.append(currentMail,ignore_index=True)

            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print(e," : mail ignoré")
                mails_dropped.append(file)

    print(len(mails_dropped), 'mails ignorés :', mails_dropped)
    return df

def writeFirstDataset(path,output):
    #path variable is the path to the mail folders
    df = Parser(path)
    with open(output,'w',encoding='utf-16') as csvfile:
        df.to_csv(csvfile,sep='¤',quotechar='§')

def WriteFinalDataset(path,inputFile,outputFile):
    os.system('cls')
    if not os.path.isfile(os.path.join(os.getcwd(),inputFile)):
        print("Ecriture des données ...")
        writeFirstDataset(path,inputFile)
    
    print(f"Lecture de {inputFile} ...")
    data = pd.read_csv(inputFile,sep='¤',quotechar='§',encoding='UTF-16', engine='python',header=0,skipinitialspace=True,dtype=str)

    print("Traitement des données ...")
    output_data = lemmatizeDF(data)

    print(f"Ecriture de {outputFile} ...")
    output_data.to_csv(outputFile,encoding='UTF-16')

if __name__=='__main__':
    path = r'\\HM.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail'
    WriteFinalDataset(path,'firstdataset2.csv','finaldataset2.csv')