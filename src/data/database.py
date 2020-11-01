import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.constants import DATABASE
from src.data import entities as en
import sqlalchemy.orm.session

engine = create_engine(f'sqlite+pysqlite:///{DATABASE}')
Session = sessionmaker(bind=engine)


@contextmanager
def create_connection(db_file: Path) -> sqlite3.Connection:
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
def get_session() -> sqlalchemy.orm.session.Session:
    session = None
    try:
        session = Session()
        yield session
    finally:
        if session is not None:
            session.close()


def get_links_as_dataframe() -> pd.DataFrame:
    with create_connection(DATABASE) as conn:
        return pd.read_sql_query("select * from urls;", conn)


def get_links(session) -> List[en.URL]:
    return session.query(en.URL).all()


def get_url_attributes(id: int = None) -> List[en.URLAttributes]:
    with get_session() as session:
        url_attributes = session.query(en.URLAttributes)
        if id is None:
            return url_attributes.all()
        return url_attributes.filter(en.URLAttributes.url_id == id).all()


