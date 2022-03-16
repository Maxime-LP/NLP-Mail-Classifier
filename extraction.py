# -*- coding: utf-8 -*-           
import os
from collections import defaultdict
import pandas as pd
import extract_msg
import multiprocessing as mp

def isThisASupportMail(message, directory, sender):
    if directory == 'Non assistance' or message.subject.lower()[:3] == 're:' or message.subject.lower()[:4] == 're :' or \
    message.subject.lower()[:5] == '[toc]' or sender in ['chable brice', 'favreliere david', 'plonquet nadège', 'courtais yohan', 'le paumier maxime']:
        return 0
    elif directory == 'Assistance + réponses':
        return 1
    else:
        return 2

def isThisASupportMail_v2(message, directory, sender):
    if directory == 'Non assistance' or message.subject.lower()[:5] == '[toc]':
        return 0
    elif directory == 'Assistance + réponses':
        return 1
    else:
        return 2

def TruncBody(txt):
    messageBodyList = txt.split('\n')
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

def ExtractInfo(filepath):
    message = extract_msg.Message(filepath, delayAttachments = True)
    directory = filepath.split('\\')[-2]
    mail = defaultdict(str)
    mail['header'] = message.subject.lower()
    mail['body'] = TruncBody(message.body.lower())
    mail['date'] = message.date
    mail['from'] = message.sender.lower()
    mail['label'] = isThisASupportMail_v2(message, directory, mail['from'])
    return mail

def ReadMail(filepath):
    try:
        return ExtractInfo(filepath)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print(e," : mail ignoré")

def extraction(writeto, path=os.getcwd()):
    filesList = [os.path.join(root,file) for root, dir, files in os.walk(path) for file in files]
    with mp.Pool(os.cpu_count()) as p:
        mails = p.map(ReadMail, filesList)
    df = pd.DataFrame(mails)

    with open(writeto,'w', encoding='utf-16') as csvfile:
        df.to_csv(csvfile, encoding='utf-16')


if __name__ == '__main__':
    path = r"\\hm.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail"
    extraction('data/mails.csv', path)