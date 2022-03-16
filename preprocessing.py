# -*- coding: utf-8 -*-           
import re  

def CleanText(txt):
    #Removes boxes
    txt = re.sub("\[.*?\]", "", txt) #non-greedy matches
    txt = re.sub("<.*?>", "", txt)
    #Removes link markers and punctuation
    txt = re.sub("https?://|www", "", txt)
    #txt = re.sub("[\\\.…\_,;!?@:/=\"«»><\(\)\[\]#}{~°+\|£$¤€*§%]", " ", txt)
    txt = re.sub("([^\w\s]+)|(_+)", " ", txt)
    #Removes isolated numbers
    txt = re.sub(r"\b[0-9]+\b", "", txt)
    #Replaces any stack of whitespaces with a single one
    txt = re.sub("\s+", " ", txt)

    return txt
    
def clean_df(df):
    df['text'] = df[['header', 'body']].astype(str).agg(' '.join, axis=1)
    df['text'] = df['text'].apply(CleanText)
    return df

def preprocessing_df(df):
    df = clean_df(df)
    return df