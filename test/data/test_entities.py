from unittest import TestCase
from src.data import entities as en


class TestEntities(TestCase):
    def test_should_initialize_url_object(self):
        url = en.URL()
        self.assertIsNotNone(url)

    def test_should_initialize_url_attributes_object(self):
        url_attributes = en.URLAttributes()
        self.assertIsNotNone(url_attributes)
