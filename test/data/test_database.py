from unittest import TestCase

import pandas as pd

from src.constants import DATABASE
from src.data import database
from src.data import entities as en


class TestDatabase(TestCase):

    def test_should_create_new_db_when_db_does_not_exist(self):
        db_file = 'idontexist.db'
        self.assertIsNotNone(database.create_connection(db_file))

    def test_should_open_db_when_db_exists(self):
        db_file = DATABASE
        self.assertIsNotNone(database.create_connection(db_file))

    def test_should_return_links_from_db(self):
        links = database.get_links_as_dataframe()
        self.assertIsInstance(links, pd.DataFrame)
        # the assertions below follow from the fact that before article fetch there are 51 records, but after the fetch
        # attempt those articles that cannot be fetched are removed from the db and only 50 are left
        self.assertGreaterEqual(len(links), 50)
        self.assertLessEqual(len(links), 51)

    def test_should_return_links_as_objects(self):
        with database.get_session() as session:
            links = database.get_links(session)
        self.assertIsNotNone(links)
        self.assertIsInstance(links, list)
        self.assertIsInstance(links[0], en.URL)
        # the assertions below follow from the fact that before article fetch there are 51 records, but after the fetch
        # attempt those articles that cannot be fetched are removed from the db and only 50 are left
        self.assertGreaterEqual(len(links), 50)
        self.assertLessEqual(len(links), 51)

    def test_should_return_article_attributes_as_objects(self):
        articles = database.get_url_attributes()

        self.assertIsNotNone(articles)
        # one article refused to get downloaded
        self.assertEqual(50, len(articles), 'Please run `prepare_dataset.py` to load articles into the database')
        self.assertIsInstance(articles, list)
        self.assertIsInstance(articles[0], en.URLAttributes)
