# -*- coding: utf-8 -*-           
import os, re  
from collections import defaultdict
import pandas as pd
from lemmatization import lemmatizeDF
from utilities import progressbar
import extract_msg

def TruncBody(message):
    messageBodyList = message.body.splitlines(keepends=False)
    i = 0
    while True :
        try:
            if messageBodyList[i] == 'De :' and messageBodyList[i+1] == 'Envoyé :' and messageBodyList[i+2] == 'À :':
                messageBodyList = messageBodyList[0:i]
                break
        except IndexError:
            break
        i += 1
    return ' '.join(messageBodyList)

def isThisASupportMail(message, directory, sender):
    if directory == 'Non assistance' or message.subject.lower()[:3] == 're:' or message.subject.lower()[:4] == 're :' or \
    message.subject.lower()[:5] == '[toc]' or sender in ['chable brice', 'favreliere david', 'plonquet nadège', 'courtais yohan', 'le paumier maxime']:
        return 0
    elif directory == 'Assistance + réponses':
        return 1
    else:
        return 2

def ReadMail(message,directory):
    mail = defaultdict(str)
    sender = re.search('<(.+)@',str(message.sender.lower()))
    if sender is None:
        mail['sender'] = message.sender.lower()
    else:
        splits = sender.group(1).split('.')
        mail['sender'] = ' '.join([splits[-1]] + splits[0:-1])

    mail['demande_de_support'] = isThisASupportMail(message, directory, mail['sender'])

    mail['text'] = message.subject.lower() + ' ' + TruncBody(message).lower()

    #Removes boxes
    mail['text'] = re.sub("\[.*?\]", "", mail['text']) #non-greedy matches
    mail['text'] = re.sub("<.*?>", "", mail['text'])

    #Removes link markers and punctuation
    mail['text'] = re.sub("https?://|www", "", mail['text'])
    mail['text'] = re.sub("[\\\.…\_,;!?@:/=\"«»><\(\)\[\]#}{~°+\|£$¤€*§%]", " ", mail['text'])

    #Removes isolated numbers
    mail['text'] = re.sub(r"\b[0-9]+\b", "", mail['text'])

    #Replaces any stack of whitespaces with a single one
    mail['text'] = re.sub("\s+", " ", mail['text'])

    return mail

def Parser(path):
    #path > Assistance / Non assistance
    df = pd.DataFrame(data=None,columns=['demande_de_support','sender','text'])
    mails_dropped = []
    print('PATH : ',path)
    totalSteps, step = 3300, 0
    progressbar(step,totalSteps)
    for root,dirs,files in os.walk(path):
        for file in files:
            try:
                directory = root.split('\\')[-1]
                message = extract_msg.Message(os.path.join(root,file))
                currentMail = ReadMail(message,directory)
                df = df.append(currentMail,ignore_index=True)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print(e," : mail ignoré")
                mails_dropped.append(file)
            step += 1
            progressbar(step,totalSteps)

    print('\n\n', len(mails_dropped), 'mails ignorés :', mails_dropped)
    return df

def writeFirstDataset(path,output):
    #path variable is the path to the mail folders
    df = Parser(path)
    with open(output,'w',encoding='utf-16') as csvfile:
        df.to_csv(csvfile,sep='¤',quotechar='§')

def WriteFinalDataset(inputFile,outputFile,path=os.getcwd()):
    os.system('cls')
    if not os.path.isfile(os.path.join(os.getcwd(),inputFile)):
        print("Ecriture des données ...")
        writeFirstDataset(path,inputFile)
    
    print(f"Lecture de {inputFile} ...")
    #data = pd.read_csv(inputFile,sep='¤',quotechar='§',encoding='UTF-16', engine='python',header=0,skipinitialspace=True,dtype=str)

    print("Traitement des données ...")
    #output_data = lemmatizeDF(data)

    print(f"Ecriture de {outputFile} ...")
    #output_data.to_csv(outputFile,encoding='UTF-16')


if __name__ == '__main__':
    path = r"\\hm.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail"
    WriteFinalDataset('firstdataset.csv', 'finaldataset.csv', path)