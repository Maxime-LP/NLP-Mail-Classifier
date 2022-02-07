# -*- coding: utf-8 -*-           
import os, re      
from collections import defaultdict
import pandas as pd
from lemmatization import lemmatizeDF, initSpacy
import extract_msg
from sklearn.feature_extraction.text import HashingVectorizer
tokenizer = HashingVectorizer(strip_accents='unicode').build_tokenizer()

def ForwardedBodyRemover(message):
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
    if directory == 'Assistance + réponses':
        if message.subject.lower()[:3] != 're:' and message.subject.lower()[:4] != 're :' and \
        message.subject.lower()[:5] != '[toc]' and sender not in ['chable brice','plonquet nadège','courtais yohan','le paumier maxime']:
            return 1
        else:
            return 0
    elif directory == 'Non assistance':
        return 0
    elif sender in ['chable brice','plonquet nadège','courtais yohan','le paumier maxime']:
        return 0
    elif message.subject.lower()[:3] == 're:' or message.subject.lower()[:4] == 're :' or message.subject.lower()[:5] == '[toc]':
        return 0
    else:
        return 'unknown'

def ReadMail(message,directory):
    mail = defaultdict(str)

    sender = re.search('<(.+)@',str(message.sender.lower()))
    if sender is None:
        mail['sender'] = message.sender.lower()
    else:
        splits = sender.group(1).split('.')
        mail['sender'] = ' '.join([splits[-1]] + splits[0:-1])

    mail['demande_de_support'] = isThisASupportMail(message, directory, mail['sender'])

    mail['text'] = message.subject.lower() + ' ' + ForwardedBodyRemover(message).lower()
    #Removes html
    mail['text'] = re.sub("<(mailto|https?).+>","",mail['text'])
    #Removes phone numbers
    mail['text'] = re.sub("([0-9]{2}\s?){5}","",mail['text'])
    mail['text'] = re.sub("[0-9]{2}(%20[0-9]{2}){4}","",mail['text'])
    #Removes link markers
    mail['text'] = re.sub("https?|www","",mail['text'])
    #Finds the words of 2 letters or more and strips accents
    words = tokenizer(mail['text'])
    mail['text'] = ' '.join(words)
    return mail

def Parser(path):
    #path > Assistance / Non assistance
    df = pd.DataFrame(data=None,columns=['demande_de_support','sender','text'])
    mails_dropped = []

    print('PATH : ',path)
    for root,dirs,files in os.walk(path):  
        for file in files:
            try:
                directory = root.split('\\')[-1]
                message = extract_msg.Message(os.path.join(root,file))
                print(message.subject)
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
    path = r"\\hm.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail2"
    WriteFinalDataset('firstdataset.csv', 'finaldataset.csv', path)