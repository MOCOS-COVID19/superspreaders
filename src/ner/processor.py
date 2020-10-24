import itertools
from typing import List, Any

from deeppavlov import configs, build_model

from src import constants as conts


class ArticleProcessor:

    NOT_NER = 'O'
    NER_BEGIN = 'B'

    __instance = None

    def __init__(self):

        if ArticleProcessor.__instance is not None:
            raise RuntimeError('Call get_instance() instead')
        self.ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)
        ArticleProcessor.__instance = self

    @staticmethod
    def get_instance():
        """Implements a singleton pattern based on notes in
        https://medium.com/@rohitgupta2801/the-singleton-class-python-c9e5acfe106c
        and ignoring the guidelines in https://python-patterns.guide/gang-of-four/singleton/
        """
        if ArticleProcessor.__instance is None:
            ArticleProcessor()
        return ArticleProcessor.__instance

    @staticmethod
    def get_fragment(fragment, ners, tokens, idx):
        ner_type = ners[idx - 1][2:]
        if ner_type == conts.NER.CARDINAL:
            return f"{' '.join(fragment)} ({tokens[idx]}) [{ners[idx - 1][2:]}]"
        else:
            return f"{' '.join(fragment)} [{ners[idx - 1][2:]}]"

    @staticmethod
    def sanitize(sentences):
        # len(sentence_tokenizer.tokenize(sanitized[0]))
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

    @staticmethod
    def _calc_len_of_ne(named_entity_type, all_nes, token_idx):
        length = 1
        while token_idx + length < len(all_nes) and all_nes[token_idx + length] == named_entity_type:
            length += 1
        return length

    def prepare_for_classification(self, named_entity_type: str, sentences: List[str], offset: int = 16) -> List[Any]:
        """
        The function returns the whole named entity surrounded with 16 tokens from the left and 16 tokens from the right
        :param named_entity_type:
        :param sentences:
        :param offset:
        :return:
        """
        output = []
        sentences = self.sanitize(sentences)
        result = self.ner_model(sentences)
        named_entity_type = conts.ner_beginning(named_entity_type)
        named_entity_inside = conts.ner_inside(named_entity_type)

        all_tokens = [None] * offset + list(itertools.chain.from_iterable(result[0])) + [None] * offset
        all_nes = [None] * offset + list(itertools.chain.from_iterable(result[1])) + [None] * offset

        for token_idx, (token, named_entity) in enumerate(zip(all_tokens, all_nes)):

            if named_entity == named_entity_type:
                length = self._calc_len_of_ne(named_entity_inside, all_nes, token_idx)
                phrase = all_tokens[token_idx - offset:token_idx + offset + length]
                output.append(phrase)

        return output

proc = ArticleProcessor()
