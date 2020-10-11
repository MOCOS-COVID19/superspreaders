from unittest import TestCase

from src.ner import processor


class TestProcessor(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proc = processor.ArticleProcessor()

    def test_should_remove_new_lines(self):
        sanitized = self.proc.sanitize(['text\n\n\ntext'])
        self.assertEqual(['text', 'text'], sanitized)

    def test_should_return_cardinal_with_following_word(self):
        tokens = ['23', 'górników','z', 'Rudy', 'Śląskiej']
        words = ['23']
        ners = ['B-CARDINAL', 'O', 'O', 'B-NER', 'I-NER']
        result = self.proc.get_fragment(words, ners, tokens, 1)
        self.assertEqual('23 (górników) [CARDINAL]', result)

    def test_should_return_regular_ner(self):
        tokens = ['23', 'górników', 'z', 'Rudy', 'Śląskiej']
        words = ['Rudy', 'Śląskiej']
        ners = ['B-CARDINAL', 'O', 'O', 'B-NER', 'I-NER']
        result = self.proc.get_fragment(words, ners, tokens, 5)
        self.assertEqual('Rudy Śląskiej [NER]', result)

    def test_run(self):
        sentences = ['23 górników w Rudy Śląskiej', '50 lekarzy z Wrocławia']
        result = self.proc.run(sentences)
        self.assertIsNotNone(result)
        self.assertEqual(4, len(result))
        self.assertEqual('23 (górników) [CARDINAL]', result[0])
        self.assertEqual('Rudy Śląskiej [GPE]', result[1])
        self.assertEqual('50 (lekarzy) [CARDINAL]', result[2])
        self.assertEqual('Wrocławia [GPE]', result[3])

    def test_prepare_for_classification(self):
        ner_type = 'CARDINAL'
        sentences = ['23 górników z Rudy Śląskiej i członków ich rodzin z wakacji nad morzem wróciło '
                                 'z koronawirusem. Wyjazd zorganizowały związki zawodowe. Wszyscy urlopowicze '
                                 'trafili do kwarantanny. 60 osób upchniętych w autokarze. Wśród nich zakażeni '
                                 'SARS-CoV-2. Tak wyglądał wyjazd nad morze rodzin górników z Rudy Śląskiej. '
                                 'Efekt - wycieczka zmieniła się w ognisko koronawirusa, już stwierdzono zakażenie '
                                 '23 osób.']
        output = self.proc.prepare_for_classification(ner_type, sentences)
        self.assertEqual(3, len(output))
        expected0 = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                   '23', 'górników', 'z', 'Rudy', 'Śląskiej', 'i', 'członków', 'ich', 'rodzin', 'z', 'wakacji',
                   'nad', 'morzem', 'wróciło', 'z', 'koronawirusem', '.']
        expected1 = ['morzem', 'wróciło', 'z', 'koronawirusem', '.', 'Wyjazd', 'zorganizowały', 'związki', 'zawodowe',
                     '.', 'Wszyscy', 'urlopowicze', 'trafili', 'do', 'kwarantanny', '.', '60', 'osób', 'upchniętych',
                     'w', 'autokarze', '.', 'Wśród', 'nich', 'zakażeni', 'SARS', '-', 'CoV', '-', '2', '.', 'Tak',
                     'wyglądał']
        expected2 = ['z', 'Rudy', 'Śląskiej', '.', 'Efekt', '-', 'wycieczka', 'zmieniła', 'się', 'w', 'ognisko',
                     'koronawirusa', ',', 'już', 'stwierdzono', 'zakażenie', '23', 'osób', '.', None, None, None, None,
                     None, None, None, None, None, None, None, None, None, None]
        self.assertEqual(33, len(output[0]))
        self.assertEqual('23', output[0][16])
        self.assertEqual(expected0, output[0])
        self.assertEqual(33, len(output[1]))
        self.assertEqual('60', output[1][16])
        self.assertEqual(expected1, output[1])
        self.assertEqual(33, len(output[2]))
        self.assertEqual('23', output[2][16])
        self.assertEqual(expected2, output[2])
