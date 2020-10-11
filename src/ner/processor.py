from typing import List, Any
from deeppavlov import configs, build_model
from collections import deque
import itertools


class ArticleProcessor:
    CARDINAL = 'CARDINAL'
    NOT_NER = 'O'
    NER_BEGIN = 'B'

    def __init__(self):
        self.ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)

    @staticmethod
    def get_fragment(fragment, ners, tokens, idx):
        ner_type = ners[idx - 1][2:]
        if ner_type == ArticleProcessor.CARDINAL:
            return f"{' '.join(fragment)} ({tokens[idx]}) [{ners[idx - 1][2:]}]"
        else:
            return f"{' '.join(fragment)} [{ners[idx - 1][2:]}]"

    @staticmethod
    def sanitize(sentences):
        sanitized = []
        for sentence in sentences:
            sanitized.extend(sentence.split('\n'))
        return [sentence for sentence in sanitized if len(sentence) > 0]

    def run(self, sentences: List[str]):
        sentences = self.sanitize(sentences)
        result = self.ner_model(sentences)

        fragments = []
        for sentence_idx, (tokens, ners) in enumerate(zip(result[0], result[1])):
            sentence_len = len(tokens)
            idx = 0
            words = []
            while idx < sentence_len:
                if ners[idx] == self.NOT_NER or ners[idx].startswith(self.NER_BEGIN):
                    if len(words) > 0:
                        fragments.append(self.get_fragment(words, ners, tokens, idx))
                    words.clear()
                    if ners[idx].startswith(self.NER_BEGIN):
                        words.append(tokens[idx])
                else:
                    words.append(tokens[idx])
                idx += 1
            if len(words) > 0:
                fragments.append(self.get_fragment(words, ners, tokens, idx))
        return fragments

    def prepare_for_classification(self, ner_type: str, sentences: List[str], offset: int = 16)-> List[Any]:
        output = []
        sentences = self.sanitize(sentences)
        result = self.ner_model(sentences)
        ner_type = f'B-{ner_type}'

        all_tokens = [None] * offset + list(itertools.chain.from_iterable(result[0])) + [None] * offset
        all_ners = [None] * offset + list(itertools.chain.from_iterable(result[1])) + [None] * offset

        for token_idx, (token, ner) in enumerate(zip(all_tokens, all_ners)):

            if ner == ner_type:
                phrase = all_tokens[token_idx-offset:token_idx+offset+1]
                output.append(phrase)

        return output
