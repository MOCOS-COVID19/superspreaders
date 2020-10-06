import sqlite3
from sqlite3 import Error
from contextlib import contextmanager

import pandas as pd

from constants import DATABASE


@contextmanager
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        yield conn
    finally:
        if conn is not None:
            conn.close()


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
    except Error as e:
        print(e)


def make_database():
    sql_create_urls_table = """CREATE TABLE IF NOT EXISTS urls 
                            (id integer PRIMARY KEY, 
                            search_text text, 
                            url text); """

    sql_create_urls_attributes_table = """CREATE TABLE IF NOT EXISTS urls_attributes (
                                    id integer PRIMARY KEY,
                                    url_id ineger not null, 
                                    authors blob,
                                    date_download date,
                                    date_modify date,
                                    date_publish text,
                                    description text,
                                    filename text,
                                    language varchar (10),
                                    localpath text,
                                    title text,
                                    title_page text,
                                    title_rss text,
                                    source_domain text,
                                    maintext blob,
                                    FOREIGN KEY (url_id) REFERENCES urls (id));"""

    # create a database connection
    with create_connection(DATABASE) as conn:

        # create url table
        create_table(conn, sql_create_urls_table)

        # create url_attributes table
        create_table(conn, sql_create_urls_attributes_table)


def get_links():
    with create_connection(DATABASE) as conn:
        return pd.read_sql_query("select * from urls;", conn)
