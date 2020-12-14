import csv
import itertools
import re
import string
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from stempel import StempelStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score

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


def train_test_split(X, y, train_size=0.75, stratify=True, random_state=None):
    random = np.random.default_rng(random_state)
    if not stratify:
        raise ValueError('Only stratification is supported at the moment')
    class0 = np.where(y == 0)[0]
    class1 = np.where(y == 1)[0]
    train0 = random.choice(class0, size=int(np.round(train_size * len(class0))))
    train1 = random.choice(class1, size=int(np.round(train_size * len(class1))))
    train = np.sort(np.concatenate((train0, train1)))
    test0 = np.setdiff1d(class0, train0)
    test1 = np.setdiff1d(class1, train1)
    test = np.sort(np.concatenate((test0, test1)))
    return [X[idx] for idx in train], [X[idx] for idx in test], y[train], y[test]


def logistic_regression_tfidf(X, y, lower: bool = False,
                              ngram_range=(1, 1), dual=False, random_state=2020):
    print(f'Logistic regresion with tfidf, lowercase: {lower}, ngram range: {ngram_range}, dual: {dual}')

    class Joiner:
        @staticmethod
        def fit_transform(texts, y):
            return [' '.join(text) for text in texts]

        @staticmethod
        def transform(texts):
            return [' '.join(text) for text in texts]

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.75, stratify=True, random_state=random_state)
    stratified_k_fold = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    parameters = {'logisticregression__C': [1e-8, 1e-4, 0.1, 1, 2, 5, 8, 13, 21, 34, 50, 100, 1000]}
    classifier_pipeline = make_pipeline(Joiner(),
                                        TfidfVectorizer(lowercase=lower, ngram_range=ngram_range),
                                        LogisticRegression(solver='lbfgs', class_weight='balanced'))  # , C=25, max_iter=500,
    clf = GridSearchCV(classifier_pipeline, parameters, cv=stratified_k_fold, scoring='f1_macro',
                       return_train_score=True)
    # classifier_pipeline.fit(X_train, y_train)
    clf.fit(X_train, y_train)
    results = clf.cv_results_
    print(results.get('params'))
    print(results.get('mean_train_score'))
    print(results.get('mean_test_score'))
    print(clf.best_params_)
    print(clf.best_score_)
    print(f1_score(y_train, clf.predict(X_train), average='macro'))
    # print(f1_score())

    print(f1_score(y_test, clf.predict(X_test), average='macro'))

    classifier_pipeline = make_pipeline(Joiner(),
                                        TfidfVectorizer(lowercase=lower, ngram_range=ngram_range),
                                        LogisticRegression(solver='lbfgs',
                                                           class_weight='balanced', C=0.01))  # , max_iter=500,
    classifier_pipeline.fit(X_train, y_train)
    print(f1_score(y_train, classifier_pipeline.predict(X_train), average='macro'))
    print(f1_score(y_test, classifier_pipeline.predict(X_test), average='macro'))

    # scores = cross_val_score(classifier_pipeline, X, y, cv=stratified_k_fold, scoring='f1_macro')
    # print(f'F1 macro scores: {scores}')
    # print(f'Average F1 macro score {np.mean(scores)}')


def main(X, y, offset=16):
    kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=2020)
    for lower in [False, True]:
        # logistic_regression_one_hot(X, y, kfold, offset, lower)
        # logistic_regression_one_hot(X, y, kfold, offset, lower, True)
        # logistic_regression_one_hot(X, y, kfold, offset, lower, True, True)
        logistic_regression_tfidf(X, y, lower)
        logistic_regression_tfidf(X, y, lower, ngram_range=(1, 3))
        logistic_regression_tfidf(X, y, lower, ngram_range=(2, 5))


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
    X_train, y_train, X_test, y_test = train_test_split(X, y, train_size=0.75, stratify=True)
    logistic_regression_tfidf(X, y)
