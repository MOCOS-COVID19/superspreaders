import logging
from typing import List
from datetime import datetime

from newspaper.article import ArticleDownloadState

from src.data.database import get_links, get_session, get_url_attributes
from src.data.entities import URLAttributes, URL
from src.ner import processor
from src.webscrapping.downloader import fetch_with_newspaper


def load_articles(links: List[URL]) -> None:
    with get_session() as session:
        for link in links:
            article = fetch_with_newspaper(link.url)
            if article.download_state == ArticleDownloadState.SUCCESS:
                attributes = URLAttributes()
                attributes.url = link
                attributes.title = article.title
                attributes.authors = ';'.join(article.authors)
                attributes.date_publish = article.publish_date
                attributes.date_download = datetime.now()
                attributes.date_modify = None
                attributes.description = article.meta_description
                attributes.maintext = article.text
                attributes.source_domain = article.source_url
                session.add(attributes)
                logging.info(f'{article.url} downloaded and saved')
        session.commit()


def retrieve_named_entities(articles):
    proc = processor.ArticleProcessor()
    for article in articles:
        information = proc.run([article.title, article.meta_description, article.text])
        print(information)
        break


def main():
    load_articles(get_links())
    retrieve_named_entities(get_url_attributes())


if __name__ == '__main__':
    retrieve_named_entities(get_url_attributes())
