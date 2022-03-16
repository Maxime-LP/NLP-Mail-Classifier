# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
import pandas as pd
import os, spacy, re
from unidecode import unidecode

def initSpacy(spacyModule):
    try:
        lemmatizer = spacy.load(spacyModule, disable = ['parser', 'attribute_ruler', 'ner'])
    except OSError:
        print('Module introuvable. Téléchargement en cours ...')
        os.system(f'python -m spacy download {spacyModule} >nul 2>&1')
        lemmatizer = spacy.load(spacyModule)
    return lemmatizer

def lemmatizeRow(inputText, lemmatizer):    
    doc = lemmatizer(inputText)
    word_lemmas_list = [unidecode(token.lemma_.lower().strip()) for token in doc if not token.is_stop and token.lemma_ != "-PRON-" and re.match('^\w{2,}$', token.lemma_.lower()) is not None]    
    bigram_list = [ word_lemmas_list[i] + "_" + word_lemmas_list[i+1] for i in range(0, len(word_lemmas_list)-1)]
    return ' '.join(word_lemmas_list + bigram_list)

def lemmatizeDf(df, input_col='text'):
    lemmatizer = initSpacy('fr_core_news_md')
    df[input_col + '_lem'] = df[input_col].apply(lambda row: lemmatizeRow(row[input_col], lemmatizer))
    return df

def countWordsSentence(sentence):
        word_list = sentence.split(' ')
        outputDict = dict(Counter(word_list))
        return outputDict

def ohe_df(input_df, input_col = 'text'):
    #Apply one hot encoding to a lemmatized text dataframe
    tokens = defaultdict(list)
    df = input_df[['label']].copy()
    df['text'] = input_df[input_col]

    for step,text in enumerate(df[input_col]):
        if type(text)==str:
            for word,count in countWordsSentence(text).items():
                tokens[word] += [0]*(step-len(tokens[word])) + [count]

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    output_df['demande_de_support'] = df['label']

    return output_df