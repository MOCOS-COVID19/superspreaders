import logging
from datetime import datetime

from newspaper.article import ArticleDownloadState

from src.data.database import get_links, get_session
from src.data.entities import URLAttributes
from src.webscrapping.downloader import fetch_with_newspaper


def main():
    with get_session() as session:
        for link in get_links():
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


if __name__ == '__main__':
    main()
