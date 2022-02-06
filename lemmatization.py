# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
import pandas as pd
import os, sys, spacy, re
from sklearn.feature_extraction.text import CountVectorizer



############################################################################
def initSpacy(spacyModule):
    try:
        lemmatizer = spacy.load(spacyModule, disable = ['parser', 'attribute_ruler', 'ner'])
    except OSError:
        print('Module introuvable. Téléchargement en cours ...')
        os.system(f'python -m spacy download {spacyModule} >nul 2>&1')
        lemmatizer = spacy.load(spacyModule)
    return lemmatizer

def lemmatizer(inputText, spacynlp):    
    doc = spacynlp(inputText)
    words_lemmas_list = [token.lemma_.lower() for token in doc if not token.is_stop and re.match('^[a-z]+$', token.lemma_.lower()) is not None]
    outputDict = dict(Counter(words_lemmas_list))
    
    newText = ' '.join(words_lemmas_list)
    ngrams_counter = nGrams(newText, nrange = (2,2))
    outputDict.update(ngrams_counter)
    return outputDict

def nGrams(inputText, nrange = (2,2)):
    inputList = list(inputText)
    Vect = CountVectorizer(analyzer='char_wb',encoding='utf-16',strip_accents='unicode',ngram_range=nrange)
    X = Vect.fit(inputList)
    return {key:1 for key in Vect.get_feature_names()}
############################################################################

def progressbar(step,totalSteps, size=60):
    x = int(size*step/totalSteps)
    sys.stdout.flush()
    sys.stdout.write("[%s%s] %i/%i\r" % ("#"*x, "."*(size-x), step, totalSteps))

def lemmatizeDF(df):
    tokens = defaultdict(list)
    totalSteps = len(df.text)
    spacynlp = initSpacy('fr_core_news_md')
    progressbar(0,totalSteps)

    for step,rawText in enumerate(df.text):
        if type(rawText)==str:
            for word,count in lemmatizer(rawText, spacynlp).items():
                tokens[word] += [0]*(step-len(tokens[word])) + [count]
            progressbar(step+1,totalSteps)
            sys.stdout.flush()

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    sys.stdout.write('\n')
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    output_df['demande_de_support'] = df['demande_de_support']
    output_df['attached_files'] = df['attached_files']

    return output_df   