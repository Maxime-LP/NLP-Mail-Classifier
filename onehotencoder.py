# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
import pandas as pd
import os, spacy, re
from sklearn.feature_extraction.text import CountVectorizer
import tqdm
from unidecode import unidecode

def initSpacy(spacyModule):
    try:
        lemmatizer = spacy.load(spacyModule, disable = ['parser', 'attribute_ruler', 'ner'])
    except OSError:
        print('Module introuvable. Téléchargement en cours ...')
        os.system(f'python -m spacy download {spacyModule} >nul 2>&1')
        lemmatizer = spacy.load(spacyModule)
    return lemmatizer

def countLemmas(inputText, lemmatizer):    
    doc = lemmatizer(inputText)
    words_lemmas_list = [unidecode(token.lemma_.lower()) for token in doc if not token.is_stop and re.match('^\w{2,}$', token.lemma_.lower()) is not None]
    outputDict = dict(Counter(words_lemmas_list))
    
    #bigrams_list = [ words_lemmas_list[i] + " " + words_lemmas_list[i+1] for i in range(0, len(words_lemmas_list)-1)]
    #outputDict.update(dict(Counter(bigrams_list)))

    return outputDict

def ohe_df(input_df):
    tokens = defaultdict(list)
    df = input_df[['label']].copy()
    df['text'] = input_df[['header', 'body']].astype(str).agg(' '.join, axis=1)

    lemmatizer = initSpacy('fr_core_news_md')

    for step,rawText in enumerate(df.text):
        if type(rawText)==str:
            for word,count in countLemmas(rawText, lemmatizer).items():
                tokens[word] += [0]*(step-len(tokens[word])) + [count]

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    output_df['demande_de_support'] = df['label']

    return output_df