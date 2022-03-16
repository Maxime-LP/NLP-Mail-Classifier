from collections import defaultdict, Counter

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