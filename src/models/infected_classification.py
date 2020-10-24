from src.constants import Classification
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import itertools
from nltk import word_tokenize
import xlrd
import re
import string
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import fbeta_score
from sklearn import preprocessing


number_pattern = re.compile(r'\d+')
num_token = '<number>'
punctuation_token = '<punctuation>'
empty_token = '<empty>'


def my_word_tokenize(doc, offset):
    output = ['<empty>'] * (offset * 2 + 1)
    tokens = word_tokenize(doc, language='polish')
    for idx, token in enumerate(tokens):
        if number_pattern.match(token):
            output[idx] = num_token
        elif token in string.punctuation:
            output[idx] = punctuation_token
        else:
            output[idx] = token
    return output


def one_hot_encode(docs, offset=16):
    # source: https://stackoverflow.com/questions/30361118/one-hot-encoding-for-representing-corpus-sentences-in-python

    # split documents to tokens
    tokens_docs = [my_word_tokenize(doc, offset) for doc in docs]
    # only keep those that are 33 tokens long and remove the middle element (a number)

    tokens_docs = [doc[:offset] + doc[-offset:] for doc in tokens_docs]
    # consider removing punctuation and replacing numbers with <num>

    # convert list of of token-lists to one flat list of tokens
    # and then create a dictionary that maps word to id of word,
    # like {A: 1, B: 2} here
    all_tokens = itertools.chain.from_iterable(tokens_docs)
    word_to_id = {token: idx for idx, token in enumerate(set(all_tokens))}

    # convert token lists to token-id lists, e.g. [[1, 2], [2, 2]] here
    token_ids = [[word_to_id[token] for token in tokens_doc] for tokens_doc in tokens_docs]

    # convert list of token-id lists to one-hot representation
    vec = OneHotEncoder(n_values=len(word_to_id))
    X = vec.fit_transform(token_ids)

    return X, correct_samples


if __name__ == '__main__':
    df = pd.read_excel(Classification.CARDINAL_MARKED_PATH)
    df = df[df['class'].isin((0,1))]

    df = df.iloc[:10]
    X, not_to_remove = one_hot_encode(df['text'].values)
    y = df.iloc[not_to_remove]['class']
    X_train, X_test, y_train, y_test = train_test_split(X.toarray(), y, test_size=0.25, stratify=y)
    le = preprocessing.LabelEncoder()
    y_train2 = le.fit_transform(y_train)
    y_test2 = le.transform(y_test)
    clf = LogisticRegression().fit(X_train, y_train2)
    y_pred = clf.predict(X_test)
    print(fbeta_score(y_test2, y_pred, beta=2))
    print(fbeta_score(y_test2, y_pred, beta=1))
