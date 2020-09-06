from unittest import TestCase
from deeppavlov import configs, build_model


ner_types = ['PERSON', 'NORP', 'FACILITY', 'ORGANIZATION', 'GPE', 'LOCATION', 'PRODUCT', 'EVENT',
                 'WORK OF ART', 'LAW', 'LANGUAGE', 'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL',
                 'CARDINAL']
not_ner = 'O'
begin_ner = 'B'
inside_ner = 'I'


def print_fragment(fragment, ners, tokens, idx):
    if len(fragment) > 0:
        ner_type = ners[idx - 1][2:]
        if ner_type == 'CARDINAL':
            print(' '.join(fragment), f'({tokens[idx]}) {ners[idx - 1][2:]}')
        else:
            print(' '.join(fragment), ners[idx - 1][2:])


class TestNerOntonotesBertMult(TestCase):
    """
    Investigation of posibilities of finding named entities within Polish news using Deep Pavlov and their pretrained
    multi-language BERT model http://docs.deeppavlov.ai/en/master/features/models/ner.html#ner-multi-bert
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)

    def test2(self):
        result = self.ner_model(['Do Nowego Sącza dotarły już wszystkie wyniki badań pensjonariuszy oraz '
                                 'pracowników jednego z Domów Pomocy Społecznej przy ul. Nawojowskiej w Nowym Sączu, '
                                 'w którym wykryto ognisko koronawirusa. - Łącznie wykonano 275 testów – mówi Luiza '
                                 'Piątkiewicz, dyrektor Miejskiego Ośrodka Pomocy Społecznej w Nowym Sączu. – '
                                 'Spośród tych osób mamy 16 pracowników oraz 70 mieszkańców z potwierdzonym '
                                 'dodatnim wynikiem.',
                                 '23 górników z Rudy Śląskiej i członków ich rodzin z wakacji nad morzem wróciło '
                                 'z koronawirusem. Wyjazd zorganizowały związki zawodowe. Wszyscy urlopowicze '
                                 'trafili do kwarantanny. 60 osób upchniętych w autokarze. Wśród nich zakażeni '
                                 'SARS-CoV-2. Tak wyglądał wyjazd nad morze rodzin górników z Rudy Śląskiej. '
                                 'Efekt - wycieczka zmieniła się w ognisko koronawirusa, już stwierdzono zakażenie '
                                 '23 osób.'
                                 ])
        tokens_list = result[0]
        ners_list = result[1]

        for sentence_idx, (tokens, ners) in enumerate(zip(tokens_list, ners_list)):
            print(f'\nSentence {sentence_idx+1}')
            sentence_len = len(tokens)
            idx = 0
            fragment = []
            while idx < sentence_len:
                if ners[idx] == not_ner:
                    print_fragment(fragment, ners, tokens, idx)
                    fragment.clear()
                    idx += 1
                    continue
                fragment.append(tokens[idx])
                idx += 1
            print_fragment(fragment, ners, tokens, sentence_len-1)
