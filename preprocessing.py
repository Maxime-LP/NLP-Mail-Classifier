# -*- coding: utf-8 -*-           
import re, os
from unidecode import unidecode
from collections import Counter, defaultdict
import stanza
from spacy.lang.fr.stop_words import STOP_WORDS
from multiprocessing import  Pool
from functools import partial
import numpy as np
import pandas as pd

POS_keys = ['AJD', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X']

def CountQuestionMarks(txt):
    txt = re.sub('\?+', r' ? ', txt)
    return len(txt.split('?'))-1

def CleanText(txt):
    txt = txt.lower()
    #Removes boxes
    txt = re.sub("\[.*?\]", " ", txt) #non-greedy matches
    txt = re.sub("<.*?>", " ", txt)

    #Removes link markers and punctuation
    txt = re.sub("https?://|www", " ", txt)
    txt = re.sub("([^\.\?!\w\s]+)|(_+)", " ", txt)

    #Replaces any combinaison of . ? ! with a single . (for further pre processing)
    txt = re.sub("[\.\?!]+", ".", txt)

    #Replaces any stack of whitespaces with a single one (for regex consistency)
    txt = re.sub("\s+", " ", txt)

    #Removes addresses
    txt = re.sub(r'\d* (rue|avenue|boulevard|route|chemin) [a-zÀ-ÿ\d ]+ ?(cs \d{5} )? ?\d{5} ?[a-zÀ-ÿ]+ ?((cedex|cx) [\d]+)?', " ", txt)

    #Removes words with letters AND numbers
    txt = re.sub(r"\b\w*(([a-z]+\d+)|(\d+[a-z]+))+\w*\b", " ", txt)

    #Remove some arbitrary words
    txt = re.sub('harmonie mutuelle (fr )?', " ", txt)

    #Replaces any stack of whitespaces with a single one (for regex consistency)
    txt = re.sub("\s+", " ", txt)

    #Removes phone numbers
    txt = re.sub(r"(0|33)[1-9]( *\d{2}){4}", " ", txt)

    txt = re.sub("\s+", " ", txt)

    return txt

def lemmatizeRow(inputText, lemmatizer):
    inputText = inputText.lower()
    doc = lemmatizer(inputText)
    words = [token for sentence in doc.sentences for token in sentence.words]
    #POS recognition
    pos = [token.upos for token in words ]
    pos_counter = defaultdict(int)
    pos_counter.update(Counter(pos))
    #sentiment analysis
    #sentiment = doc.sentiment
    #lemmatization
    words = [token for token in words if (token.lemma not in STOP_WORDS and re.match('^\w{2,20}$', token.lemma.lower()) is not None)]
    lemmas = [unidecode(token.lemma) for token in words if token.upos != "NUM"]
    return [' '.join(lemmas)] + [pos_counter[key] for key in POS_keys]

# def lemmatize_df(df, input_col='text'):
#     lemmatizer = stanza.Pipeline(lang='fr', processors='tokenize,mwt,pos,lemma', logging_level='FATAL')
#     df2 = df.apply(lambda row: lemmatizeRow(row[input_col], lemmatizer), axis = 1, result_type = 'expand')
#     df2.columns = [input_col + '_lem'] + ['_'+key+'_count_' for key in POS_keys]
#     df = pd.concat([df, df2], axis = 1)
#     df['unique_words_count'] = [len(df[input_col + '_lem'].loc[k]) for k in range(len(df[input_col + '_lem']))]
#     return df

def preprocessing_df(input_df):
    df = input_df.copy()
    input_col='text'
    df[input_col] = df[['header', 'body']].astype(str).agg(' '.join, axis=1)
    df['_questionmark_count_'] = df[input_col].apply(CountQuestionMarks)
    df[input_col] = df[input_col].apply(CleanText)
    df = df.drop(['header','body'], axis = 1)
    df = df.drop_duplicates().reset_index()

    lemmatizer = stanza.Pipeline(lang='fr', processors='tokenize,mwt,pos,lemma', logging_level='FATAL')
    df2 = df.apply(lambda row: lemmatizeRow(row[input_col], lemmatizer), axis = 1, result_type = 'expand')
    df2.columns = [input_col + '_lem'] + ['_'+key+'_count_' for key in POS_keys]
    df = pd.concat([df, df2], axis = 1)
    df['unique_words_count'] = [len(df[input_col + '_lem'].loc[k]) for k in range(len(df[input_col + '_lem']))]

    return df