from unittest import TestCase
from deeppavlov import configs, build_model


class TestNerOntonotesBertMult(TestCase):

    def test1(self):
        ner_model = build_model(configs.ner.ner_ontonotes_bert_mult, download=True)
        result = ner_model(['23 górników z Rudy Śląskiej i członków ich rodzin z wakacji nad morzem wróciło z koronawirusem. '
                            'Wyjazd zorganizowały związki zawodowe. Wszyscy urlopowicze trafili do kwarantanny. 60 osób upchniętych w autokarze. Wśród nich zakażeni SARS-CoV-2. '
                            'Tak wyglądał wyjazd nad morze rodzin górników z Rudy Śląskiej. Efekt - wycieczka zmieniła się w ognisko koronawirusa, już stwierdzono zakażenie 23 osób.'])
        for token, ner in zip(result[0], result[1]):
            print(token, ner)
