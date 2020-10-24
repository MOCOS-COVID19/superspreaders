from unittest import TestCase
from src.data.prepare_dataset import ClassificationTrainsetBuilder


class TestClassificationTrainsetBuilder(TestCase):

    def test_get_formatting_mask_on_single_token_ne(self):
        mask = ClassificationTrainsetBuilder._get_formatting_mask(33)
        self.assertEqual(33, len(mask))
        self.assertEqual(1, sum(mask))

    def test_get_formatting_mask_on_multiple_token_ne(self):
        mask = ClassificationTrainsetBuilder._get_formatting_mask(36)
        self.assertEqual(36, len(mask))
        self.assertEqual(4, sum(mask))
