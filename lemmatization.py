# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
import pandas as pd
import os, spacy, re
from sklearn.feature_extraction.text import CountVectorizer
from utilities import progressbar
from unidecode import unidecode

def initSpacy(spacyModule):
    try:
        lemmatizer = spacy.load(spacyModule, disable = ['parser', 'attribute_ruler', 'ner'])
    except OSError:
        print('Module introuvable. Téléchargement en cours ...')
        os.system(f'python -m spacy download {spacyModule} >nul 2>&1')
        lemmatizer = spacy.load(spacyModule)
    return lemmatizer

def lemmatizeText(inputText, lemmatizer):    
    doc = lemmatizer(inputText)
    words_lemmas_list = [unidecode(token.lemma_.lower()) for token in doc if not token.is_stop and re.match('^\w+$', token.lemma_.lower()) is not None]
    outputDict = dict(Counter(words_lemmas_list))
    
    #newText = ' '.join(words_lemmas_list)
    #ngrams_counter = nGrams(newText, nrange = (2,2))
    #outputDict.update(ngrams_counter)
    return outputDict

def lemmatizeDF(df):
    tokens = defaultdict(list)
    totalSteps = len(df.text)
    lemmatizer = initSpacy('fr_core_news_md')
    progressbar(0,totalSteps)

    for step,rawText in enumerate(df.text):
        if type(rawText)==str:
            for word,count in lemmatizeText(rawText, lemmatizer).items():
                tokens[word] += [0]*(step-len(tokens[word])) + [count]
            progressbar(step+1,totalSteps)

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    print('\n\n')
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    output_df['demande_de_support'] = df['demande_de_support']

    return output_df   