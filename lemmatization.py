# -*- coding: utf-8 -*-
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