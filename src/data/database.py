import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

import pandas as pd

from src.constants import DATABASE
from src.data import entities as en


engine = create_engine(f'sqlite+pysqlite:///{DATABASE}')
Session = sessionmaker(bind=engine)


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


@contextmanager
def get_session():
    session = None
    try:
        session = Session()
        yield session
    finally:
        if session is not None:
            session.close()


def get_links_as_dataframe():
    with create_connection(DATABASE) as conn:
        return pd.read_sql_query("select * from urls;", conn)


def get_links():
    with get_session() as session:
        return session.query(en.URL).all()


