# -*- coding: utf-8 -*-
import sparknlp
from sparknlp.base import *
from sparknlp.annotator import *
from pyspark.ml import Pipeline
from collections import Counter, defaultdict
import pandas as pd
import os, sys, atexit, csv, spacy
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

############################################################################
r"""
os.environ['HADOOP_HOME'] = r"C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\hadoop"
#os.environ['SPARK_HOME'] = r'C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\pyspark'
os.environ['SPARK_HOME'] =  r"C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\hadoop"
os.environ['JAVA_HOME'] = r'C:\Progra~1\OpenJDK\jdk-11.0.8.10-hotspot'
os.environ['PYSPARK_SUBMIT_ARGS'] = r'C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\pyspark-shell'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'ipython'
sys.path.append(r"C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\pyspark\bin")
"""

#sc = sparknlp.start()

def SparkNLP(input_text):
    input_text = pd.DataFrame({'input_text':[input_text]})
    #input_text = sc.createDataFrame(input_text)
    documentAssembler = DocumentAssembler().setInputCol('input_text').setOutputCol('document')
    tokenizer = Tokenizer().setInputCols(["document"]).setOutputCol("tokenized")
    normalizer = Normalizer().setInputCols(["tokenized"]).setOutputCol('normalized')
    lemmatizer = LemmatizerModel.pretrained(name="lemma", lang="fr").setInputCols(["normalized"]).setOutputCol("lemmatized")
    #stop_words = StopWordsCleaner.pretrained("stopwords_fr", "fr").setInputCols(["lemmatized"]).setOutputCol("cleanTokens")
    finisher = Finisher().setInputCols(['lemmatized'])
    
    pipeline = Pipeline().setStages([
        documentAssembler,
        tokenizer,
        normalizer,
        #lemmatizer,
        #stop_words,
        finisher
        ])

    result = pipeline.fit(input_text).transform(input_text)
    res = result.selectExpr("finished_lemmatized").show(truncate=False)
    return res

def Spacy(inputText,spacyModule='fr_dep_news_trf'):
    
    try:
        nlp = spacy.load(spacyModule)
    except OSError:
        print('Module introuvable. Téléchargement en cours ...')
        os.system(f'python -m spacy download {spacyModule} >nul 2>&1')
        nlp = spacy.load(spacyModule)

    doc = nlp(inputText)
    return dict(Counter([token.lemma_ for token in doc]))

def nGrams(inputList):
    Vect = CountVectorizer(analyzer='char_wb',encoding='utf-16',strip_accents='unicode',ngram_range=(2,10))
    X = Vect.fit_transform(inputList)
    return None

def wordsCount(inputText):
    return dict(Counter(inputText))

############################################################################

def progressbar(step,totalSteps, size=60):
    x = int(size*step/totalSteps)
    sys.stdout.flush()
    sys.stdout.write("[%s%s] %i/%i\r" % ("#"*x, "."*(size-x), step, totalSteps))

def lemmatizeDF(df,method=wordsCount):
    tokens = defaultdict(list)
    totalSteps = len(df.text)
    progressbar(0,totalSteps)

    for step,rawText in enumerate(df.text):
        if type(rawText)==str:
            text = rawText.split(' ')

            for word,count in method(text).items():
                tokens[word] += [0]*(step-len(tokens[word])) + [count]   #on a toujours step>len(tokens[word])
            
            progressbar(step+1,totalSteps)
            sys.stdout.flush()

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    sys.stdout.write('\n')
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    output_df['demande_de_support'] = df['demande_de_support']
    output_df['attached_files'] = df['attached_files']

    return output_df

#atexit.register(lambda:sc.stop())

if __name__=='__main__':
    #lemmatization('Bonjour à tous, à tous, je suis @libaba')
    Spacy('Bonjour à tous, à tous, je suis @libaba')

    