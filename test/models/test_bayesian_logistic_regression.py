from unittest import TestCase
import string
import numpy as np
from models.bayesian_logistic_regression import BayesianWeightedOneHotEncoder


class TestBayesianWeights(TestCase):

    def setUp(self):
        self.class_under_test = BayesianWeightedOneHotEncoder()
        self.class_under_test.word_to_id = {letter: idx for idx, letter in enumerate(string.ascii_letters[:14])}

    def test_should_calculate_weights(self):
        token_ids = [[12, 1, 12, 6, 4, 9, 7, 6], [0, 6, 13, 2, 5, 8, 10, 11]]
        y = np.array([1, 0])

        result = self.class_under_test.calculate_weights(token_ids, y)

        """
        p = alpha + sum_{i:y(i) = 1} f^(i)
        p = 1 + [0, 1, 0, 0, 1, 0, 2, 1, 0, 1, 0, 0, 2, 0] = [1, 2, 1, 1, 2, 1, 3, 2, 1, 2, 1, 1, 3, 1]
        q = alpha + sum_{i:y(i) = 0} f^(i)
        q = 1 + [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1] = [2, 1, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2]
        |p| = 1+2+1+1+2+1+3+2+1+2+1+1+3+1 = 22
        |q| = 2+1+2+1+1+2+2+1+2+1+2+2+1+2 = 22
        r = log10((p / |p|) / (q / |q|))
        e.g. log10((1/22)/(2/22)) = log10(0.5) = -0.301030
        """
        self.assertAlmostEqual(-0.301030, result[0])

    def test_should_count_occurrences(self):
        token_ids = [[12, 1, 12, 6, 4, 9, 7, 6], [0, 6, 13, 2, 5, 8, 10, 11]]
        y = np.array([1, 0])
        result = self.class_under_test.count_occurrences(token_ids)
        self.assertIsInstance(result, np.ndarray)
        self.assertTrue(all([0, 1, 0, 0, 1, 0, 2, 1, 0, 1, 0, 0, 2, 0] == result[0]))
        self.assertTrue(all([1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1] == result[1]))

    def test_should_count_l1_norm(self):
        self.assertEqual(22, self.class_under_test.get_l1_norm([1, 2, 1, 1, 2, 1, 3, 2, 1, 2, 1, 1, 3, 1]))
        self.assertEqual(22, self.class_under_test.get_l1_norm([2, 1, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2]))

    def test_calculate_positive_odds(self):
        expected = [1, 2, 1, 1, 2, 1, 3, 2, 1, 2, 1, 1, 3, 1]
        occurrences = np.array([[0, 1, 0, 0, 1, 0, 2, 1, 0, 1, 0, 0, 2, 0], [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1]])
        y = np.array([1, 0])
        self.assertTrue(all(expected == self.class_under_test.calculate_odds(occurrences, y, 1)))

    def test_calculate_negative_odds(self):
        expected = [2, 1, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2]
        occurrences = np.array([[0, 1, 0, 0, 1, 0, 2, 1, 0, 1, 0, 0, 2, 0], [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1]])
        y = np.array([1, 0])
        self.assertTrue(all(expected == self.class_under_test.calculate_odds(occurrences, y, 0)))

