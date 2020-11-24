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
from stempel import StempelStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

from src.constants import TrainingSet1

number_pattern = re.compile(r'\d+')
num_token = '<number>'
punctuation_token = '<punctuation>'
empty_token = '<empty>'


class NoneStemmer:
    @staticmethod
    def stem(word):
        return word


class Cleaner:
    def __init__(self, offset=16, lower=False, stemming=False, polymorph=False):
        self.offset = offset
        self.vec = None
        self.word_to_id = None
        self.lower = lower
        self.stemming = stemming
        self.polymorph = polymorph
        if self.stemming:
            if self.polymorph:
                self.stemmer = StempelStemmer.polimorf()
            else:
                self.stemmer = StempelStemmer.default()
        else:
            self.stemmer = NoneStemmer()

    def clean_tokens(self, tokens):
        output = ['<empty>'] * (self.offset * 2)

        for idx, token in enumerate(tokens):
            if number_pattern.match(token):
                output[idx] = num_token
            elif token in string.punctuation:
                output[idx] = punctuation_token
            else:
                output[idx] = self.stemmer.stem(token.lower() if self.lower else token)
        return output

    def clean_docs(self, docs):
        return [self.clean_tokens(tokens_doc) for tokens_doc in docs]

    def fit_transform(self, docs, y):
        # removing punctuation and replacing numbers with <num>
        return self.clean_docs(docs)

    def transform(self, docs):
        return self.clean_docs(docs)


class SuperSpreadersOneHotEncoder:
    def __init__(self):
        self.vec = None
        self.word_to_id = None

    def fit_transform(self, tokens_docs, y):
        # source: https://stackoverflow.com/questions/30361118/
        # one-hot-encoding-for-representing-corpus-sentences-in-python

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

    def transform(self, tokens_docs):
        token_ids = [[self.word_to_id.get(token, self.out_of_vocabulary) for token in tokens_doc]
                     for tokens_doc in tokens_docs]
        return self.vec.transform(token_ids)


def logistic_regression_one_hot(X, y, stratified_k_fold: StratifiedKFold, text_offset: int, lower: bool = False,
                                stemmer: bool = False, polymorph_stemmer: bool = False):
    print(f'Logistic regression with one hot encoding, lowercase: {lower}, stemmer: {stemmer} '
          f'{"(polymorph)" if polymorph_stemmer else ""}')
    classifier_pipeline = make_pipeline(Cleaner(text_offset, lower, stemmer, polymorph_stemmer),
                                        SuperSpreadersOneHotEncoder(),
                                        LogisticRegression(solver='lbfgs', C=25, max_iter=500, class_weight='balance'))
    scores = cross_val_score(classifier_pipeline, X, y, cv=stratified_k_fold, scoring='f1_macro')
    print(f'F1 macro scores: {scores}')
    print(f'Average F1 macro score {np.mean(scores)}')


def logistic_regression_tfidf(X, y, stratified_k_fold: StratifiedKFold, lower: bool = False,
                              ngram_range=(1, 1)):
    print(f'Logistic regresion with tfidf, lowercase: {lower}, ngram range: {ngram_range}')

    class Joiner:
        @staticmethod
        def fit_transform(texts, y):
            return [' '.join(text) for text in texts]

        @staticmethod
        def transform(texts):
            return [' '.join(text) for text in texts]

    classifier_pipeline = make_pipeline(Joiner(),
                                        TfidfVectorizer(lowercase=lower, ngram_range=ngram_range),
                                        LogisticRegression(solver='lbfgs', C=25, max_iter=500, class_weight='balance'))
    scores = cross_val_score(classifier_pipeline, X, y, cv=stratified_k_fold, scoring='f1_macro')
    print(f'F1 macro scores: {scores}')
    print(f'Average F1 macro score {np.mean(scores)}')


def main(X, y, offset=16):
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=2020)
    for lower in [False, True]:
        logistic_regression_one_hot(X, y, kfold, offset, lower)
        logistic_regression_one_hot(X, y, kfold, offset, lower, True)
        logistic_regression_one_hot(X, y, kfold, offset, lower, True, True)
        logistic_regression_tfidf(X, y, kfold, lower)
        logistic_regression_tfidf(X, y, kfold, lower, ngram_range=(1, 3))
        logistic_regression_tfidf(X, y, kfold, lower, ngram_range=(2, 5))


def get_data(offset=16):
    X = []
    with TrainingSet1.X_PATH.open('r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            X.append(row[:offset] + row[-offset:])
    y = pd.read_csv(TrainingSet1.Y_PATH, header=None).values.ravel()
    return X, y


if __name__ == '__main__':
    X, y = get_data()
    main(X, y)
