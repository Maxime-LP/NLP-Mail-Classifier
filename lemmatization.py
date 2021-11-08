# -*- coding: utf-8 -*-
from preprocessing import write_csv
import sparknlp
from sparknlp.base import *
from sparknlp.annotator import *
from pyspark.ml import Pipeline
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from collections import Counter
import pandas as pd
import os, sys, atexit

r"""
os.environ['HADOOP_HOME'] = r"C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\hadoop"
#os.environ['SPARK_HOME'] = r'C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\pyspark'
os.environ['SPARK_HOME'] =  r"C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\hadoop"
os.environ['JAVA_HOME'] = r'C:\Progra~1\OpenJDK\jdk-11.0.8.10-hotspot'
os.environ['PYSPARK_SUBMIT_ARGS'] = r'C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\pyspark-shell'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'ipython'
sys.path.append(r"C:\Users\le_paumier-m\Anaconda3\Lib\site-packages\pyspark\bin")
"""

sc = sparknlp.start()

def lemmatization(input_text):

    documentAssembler = DocumentAssembler().setInputCol('input_text').setOutputCol('document')
    tokenizer = Tokenizer().setInputCols(["document"]).setOutputCol("tokenized")
    normalizer = Normalizer().setInputCols(["tokenized"]).setOutputCol('normalized')
    lemmatizer = LemmatizerModel.pretrained(name="lemma", lang="fr").setInputCols(["normalized"]).setOutputCol("lemmatized")
    stop_words = StopWordsCleaner.pretrained("stopwords_fr", "fr").setInputCols(["lemmatized"]).setOutputCol("cleanTokens")
    finisher = Finisher().setInputCols(['cleanTokens'])
    
    pipeline = Pipeline().setStages([
        documentAssembler,
        tokenizer,
        normalizer,
        lemmatizer,
        stop_words,
        finisher
        ])

    result = pipeline.fit(input_text).transform(input_text)
    res = result.selectExpr("lemma.result").show(truncate=False)
    print(res)
    return res
    
def dfReformat(df):
    output_df = pd.DataFrame({'demande_de_support':df['demande_de_support'],'attached_files':df['attached_files']},dtype=int)
    output_df['tmp'] = 1

    rawtext_df = pd.DataFrame(dtype=str)
    rawtext_df['text'] = df.object.str.cat(df.body,sep=' ').replace('.',' ').replace(',',' ').replace('  ',' ')

    for rawtext in rawtext_df.text:
        if type(rawtext)==str:
            text = rawtext.split(' ')
            tokens = {key:[val] for key,val in dict(Counter(text)).items()}
            #tokens = lemmatization(rawtext)
            tmp_df = pd.DataFrame.from_dict(tokens,dtype=int)
            tmp_df['tmp'] = 1
            output_df = output_df.merge(tmp_df,how='outer',on=['tmp'])

    return output_df.drop('tmp',axis=1).fillna(0)

def ImportData(path,file):
    os.system('cls')
    if not os.path.isfile(os.path.join(os.getcwd(),file)):
        print("Ecriture des données ...")
        write_csv(path)
    
    print("Lecture des données ...")
    data = pd.read_csv(file,sep='¤',quotechar='§',encoding='UTF-16', engine='python',header=0,skipinitialspace=True,dtype=str)
    print(data.shape())
    print("Traitement des données ...")
    #output_data = dfReformat(data)
    #print(data)
    #return output_data

path = r'\\HM.dm.ad\hmdoc\Direction Technique Assurances\Central\MOA décisionnel\DECIBEL\Suivi\Automatisation\Mail'
ImportData(path,'firstdataset.csv')


#atexit.register(lambda:sc.stop())