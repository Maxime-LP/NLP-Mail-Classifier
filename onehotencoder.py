from collections import defaultdict, Counter
import pandas as pd
from gensim.models.phrases import Phrases

def countWordsSentence(sentence):
    word_list = sentence.split(' ')
    outputDict = dict(Counter(word_list))
    return outputDict


def ohe_df_(input_df, input_col = 'text_lem'):
    #Apply one hot encoding to a lemmatized text dataframe
    tokens = defaultdict(list)
    sentences = input_df[input_col].copy()

    for step,text in enumerate(sentences):
        if type(text)==str:
            for word,count in countWordsSentence(text).items():
                tokens[word] += [0]*(step-len(tokens[word])) + [count]

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    if 'label' in input_df.columns:
        output_df['_label_'] = input_df['label']
    else:
        output_df['_label_'] = (step+1)*[2]

    return output_df

def ohe_df(input_df, input_col = 'text_lem', bigrams = False):
    #Apply one hot encoding to a lemmatized text dataframe
    tokens = defaultdict(list)
    sentences = input_df[input_col].copy()
    sentences = [sentence.split(' ') for sentence in sentences]

    if bigrams:
        bigram = Phrases(sentences)
        sentences = [bigram[line] for line in sentences]
        sentences = [bigram[line] for line in sentences]

    for step,sentence in enumerate(sentences):
        for word,count in Counter(sentence).items():
            tokens[word] += [0]*(step-len(tokens[word])) + [count]

    for word in tokens.keys():
        tokens[word] += [0]*(step+1-len(tokens[word]))
    
    output_df = pd.DataFrame.from_dict(tokens,dtype=int)
    if 'label' in input_df.columns:
        output_df['_label_'] = input_df['label']
    else:
        output_df['_label_'] = (step+1)*[2]

    return output_df