import itertools
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from typing import List, Union


class BayesianWeightedOneHotEncoder:
    """Applies to one-hot encoding"""
    def __init__(self):
        self.vec = None
        self.word_to_id = None
        self.weights = None

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
        self.weights = self.calculate_weights(token_ids, y)
        # TODO: apply weights
        self.vec = OneHotEncoder(handle_unknown='ignore')
        return self.vec.fit_transform(token_ids)

    @property
    def out_of_vocabulary(self):
        return len(self.word_to_id)

    def transform(self, tokens_docs):
        token_ids = [[self.word_to_id.get(token, self.out_of_vocabulary) for token in tokens_doc]
                     for tokens_doc in tokens_docs]
        # TODO: apply weights
        return self.vec.transform(token_ids)

    def calculate_weights(self, token_ids, y, alpha=1):
        occurrences = self.count_occurrences(token_ids)
        p = self.calculate_odds(occurrences, y, 1, alpha)
        p_l1 = self.get_l1_norm(p)
        q = self.calculate_odds(occurrences, y, 0, alpha)
        q_l1 = self.get_l1_norm(q)
        return np.log10((p / p_l1) / (q / q_l1))

    @staticmethod
    def calculate_odds(occurrences: np.ndarray, y: np.ndarray, y_value: int, alpha: Union[float, int] = 1):
        return alpha + np.sum(occurrences[np.where(y == y_value)[0]], axis=0)

    def count_occurrences(self, token_ids: List[List[int]]) -> np.ndarray:
        occurrences = []
        for current_token_ids in token_ids:
            current_occurrences = [0] * len(self.word_to_id)
            for token in current_token_ids:
                current_occurrences[token] += 1
            occurrences.append(current_occurrences)
        return np.array(occurrences)

    @staticmethod
    def get_l1_norm(vec):
        return np.sum(np.abs(vec))
