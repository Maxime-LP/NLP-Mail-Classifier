# -*- coding: utf-8 -*-           
import os
import json
import extract_msg
import multiprocessing as mp
import time

def SplitBodies(message):
    messageBodyList = message.body.splitlines()
    bodies = []
    i = 0
    while True :
        try:
            if messageBodyList[i][0:4] == 'De :' and messageBodyList[i+1][0:8] == 'Envoyé :' and messageBodyList[i+2][0:3] == 'À :':
                bodies.append(messageBodyList[0:i])
                del messageBodyList[0:i]
                i = 3
            else:
                i += 1
        except IndexError:
            bodies.append(messageBodyList[0:i])
            break
    
    return bodies

def ReadMails(filepath):
    message = extract_msg.Message(filepath, delayAttachments = True)
    directory = filepath.split('\\')[-2]
    mails = []
    first_mail = True
    bodies = SplitBodies(message)
    for body in bodies:

        if directory == 'Assistance':
            label = 1
        elif directory == 'Non assistance':
            label = 0
        else:
            label = 2
        
        if first_mail:
            if message.sender is not None:
                fro = message.sender.lower()
            else:
                fro = ""
            if message.subject is not None:
                header = message.subject.lower()
            else:
                header = ""
            first_mail = False
            for index, line in enumerate(body):
                if line[0:4] == 'De :':
                    fro = line[4::].strip()
                elif line[0:7] == 'Objet :':
                    header = line[7::].strip()
                    body = body[index+1::]
                    break
    
        mails.append({
            'header' : header,
            'body' : ' '.join(body),
            'from' : fro,
            'label' : label
        })

    return mails

def dir_to_json(path=os.path.join(os.getcwd(),'Mail')):
    filesList = [os.path.join(root,file) for root, dir, files in os.walk(path) for file in files]
    with mp.Pool(os.cpu_count()) as p:
        mail_lists = p.map(ReadMails, filesList)
    
    mails = [mail for li in mail_lists for mail in li]
    with open(os.path.join(os.getcwd(), 'data', 'mails_raw.json'), 'w', encoding='utf-16') as jsonfile:
        print('Writing json file ...')
        json.dump(mails, jsonfile, ensure_ascii = False)


if __name__ == '__main__':
    path = r"\\hm.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail"
    t = time.localtime()
    print(f'Commencé à {t.tm_hour}:{t.tm_min}:{t.tm_sec}')
    dir_to_json(path)
    t = time.localtime()
    print(f'Fini à {t.tm_hour}:{t.tm_min}:{t.tm_sec}')
