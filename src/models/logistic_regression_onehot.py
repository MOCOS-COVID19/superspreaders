import csv
import itertools
import re
import string
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from src.constants import TrainingSet1

number_pattern = re.compile(r'\d+')
num_token = '<number>'
punctuation_token = '<punctuation>'
empty_token = '<empty>'


class SuperSpreadersOneHotEncoder:
    def __init__(self, offset=16):
        self.offset = offset
        self.vec = None
        self.word_to_id = None

    def clean_tokens(self, tokens):
        output = ['<empty>'] * (self.offset * 2)
        for idx, token in enumerate(tokens):
            if number_pattern.match(token):
                output[idx] = num_token
            elif token in string.punctuation:
                output[idx] = punctuation_token
            else:
                output[idx] = token
        return output

    def fit_transform(self, docs, y):
        # source: https://stackoverflow.com/questions/30361118/one-hot-encoding-for-representing-corpus-sentences-in-python

        # removing punctuation and replacing numbers with <num>
        tokens_docs = [self.clean_tokens(tokens_doc) for tokens_doc in docs]

        # convert list of of token-lists to one flat list of tokens
        # and then create a dictionary that maps word to id of word,
        # like {A: 1, B: 2} here
        all_tokens = itertools.chain.from_iterable(tokens_docs)
        self.word_to_id = {token: idx for idx, token in enumerate(set(all_tokens))}

        # convert token lists to token-id lists, e.g. [[1, 2], [2, 2]] here
        token_ids = [[self.word_to_id[token] for token in tokens_doc] for tokens_doc in tokens_docs]

        # convert list of token-id lists to one-hot representation
        self.vec = OneHotEncoder(handle_unknown='ignore')
        return self.vec.fit_transform(token_ids)

    @property
    def out_of_vocabulary(self):
        return len(self.word_to_id)

    def transform(self, docs):
        tokens_docs = [self.clean_tokens(tokens_doc) for tokens_doc in docs]
        token_ids = [[self.word_to_id.get(token, self.out_of_vocabulary) for token in tokens_doc]
                     for tokens_doc in tokens_docs]
        return self.vec.transform(token_ids)


if __name__ == '__main__':
    X = []
    offset = 16
    with TrainingSet1.X_PATH.open('r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            X.append(row[:offset] + row[-offset:])
    y = pd.read_csv(TrainingSet1.Y_PATH, header=None).values.ravel()

    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=2020)
    classifier_pipeline = make_pipeline(SuperSpreadersOneHotEncoder(offset),
                                        LogisticRegression(solver='lbfgs', C=25, max_iter=500, class_weight='balance'))
    scores = cross_val_score(classifier_pipeline, X, y, cv=kfold, scoring='f1_macro')
    print(f'F1 macro scores: {scores}')
    print(f'Average F1 macro score {np.mean(scores)}')
