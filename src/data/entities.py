from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class URL(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    search_text = Column(Text)
    url = Column(String)


class URLAttributes(Base):
    __tablename__ = 'urls_attributes'
    id = Column(Integer, primary_key=True)
    authors = Column(String)
    date_download = Column(DateTime)
    date_modify = Column(DateTime)
    date_publish = Column(DateTime)
    description = Column(Text)
    maintext = Column(Text)
    language = Column(String)
    title = Column(String)
    source_domain = Column(String)
    url_id = Column(Integer, ForeignKey('urls.id'))
    url = relationship('URL', foreign_keys=[url_id])


class NamedEntity(Base):
    __tablename__ = 'named_entities'
    id = Column(Integer, primary_key=True)
    ner_type = Column(String)
    context_left = Column()
