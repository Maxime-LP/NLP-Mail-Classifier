# -*- coding: utf-8 -*-           
import os, re  
from collections import defaultdict
import pandas as pd
import extract_msg
import multiprocessing as mp

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

def ClearText(txt):
    #Removes boxes
    txt = re.sub("\[.*?\]", "", txt) #non-greedy matches
    txt = re.sub("<.*?>", "", txt)
    #Removes link markers and punctuation
    txt = re.sub("https?://|www", "", txt)
    #txt = re.sub("[\\\.…\_,;!?@:/=\"«»><\(\)\[\]#}{~°+\|£$¤€*§%]", " ", txt)
    txt = re.sub("([^\w\s]+)|(_+)", " ", txt)
    #Removes isolated numbers
    txt = re.sub(r"\b[0-9]+\b", "", txt)
    #Replaces any stack of whitespaces with a single one
    txt = re.sub("\s+", " ", txt)

    return txt

def isThisASupportMail(message, directory, sender):
    if directory == 'Non assistance' or message.subject.lower()[:3] == 're:' or message.subject.lower()[:4] == 're :' or \
    message.subject.lower()[:5] == '[toc]' or sender in ['chable brice', 'favreliere david', 'plonquet nadège', 'courtais yohan', 'le paumier maxime']:
        return 0
    elif directory == 'Assistance + réponses':
        return 1
    else:
        return 2

def ExtractInfo(filepath):
    message = extract_msg.Message(filepath, delayAttachments = True)
    directory = filepath.split('\\')[-2]
    mail = defaultdict(str)

    mail['body'] = TruncBody(message).lower()
    mail['body'] = ClearText(mail['body'])
    mail['header'] = ClearText(message.subject.lower())

    date = message.date
    if date is not None:
        mail['date'] = date
    else:
        mail['date'] = ''

    sender = re.search('<(.+)@',str(message.sender.lower()))
    if sender is None:
        mail['from'] = message.sender.lower()
    else:
        splits = sender.group(1).split('.')
        mail['from'] = ' '.join([splits[-1]] + splits[0:-1])

    rec = message.recipients
    if rec is not None:
        mail['to'] = ''
    else:
        mail['to'] = ''
    
    mail['label'] = isThisASupportMail(message, directory, mail['from'])
    return mail

def ReadMail(filepath):
    try:
        return ExtractInfo(filepath)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print(e," : mail ignoré")

def Parser(path, writeto):
    #path variable is the path to the mail folder
    print('PATH : ',path)
    filesList = [os.path.join(root,file) for root, dir, files in os.walk(path) for file in files]
    with mp.Pool(os.cpu_count()) as p:
        mails = p.map(ReadMail, filesList)
    df = pd.DataFrame(mails)

    with open(writeto,'w', encoding='utf-16') as csvfile:
        df.to_csv(csvfile, encoding='utf-16')

def preprocessing(firstFile, secondFile, path = os.getcwd()):
    os.system('cls')
    if not os.path.isfile(os.path.join(os.getcwd(), firstFile)):
        print("Lecture des mails ...")
        Parser(path, firstFile)

if __name__ == '__main__':
    path = r"\\hm.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail"
    preprocessing('mails.csv', path)