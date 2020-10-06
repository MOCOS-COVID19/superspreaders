from unittest import TestCase
from src.data import database
from src.constants import DATABASE
import pandas as pd


class TestDatabase(TestCase):

    def test_should_create_new_db_when_db_does_not_exist(self):
        db_file = 'idontexist.db'
        self.assertIsNotNone(database.create_connection(db_file))

    def test_should_open_db_when_db_exists(self):
        db_file = DATABASE
        self.assertIsNotNone(database.create_connection(db_file))

    def test_should_return_links_from_db(self):
        links = database.get_links()
        self.assertIsInstance(links, pd.DataFrame)
        self.assertEqual(51, len(links.index))
