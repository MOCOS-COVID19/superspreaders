import logging
from typing import List
from datetime import datetime
from pathlib import Path
import csv
from newspaper.article import ArticleDownloadState

from src.data.database import get_links, get_session, get_url_attributes
from src.data.entities import URLAttributes, URL
from src.ner import processor
from src.webscrapping.downloader import fetch_with_newspaper
from src.constants import PROCESSED_DATA_DIR


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


def retrieve_named_entities(output_file: Path, articles: List[URLAttributes], ner_type: str ='CARDINAL') -> int:
    # article processor
    proc = processor.ArticleProcessor()
    # output output csv file
    with output_file.open('w', newline='', encoding='utf-8') as csvfile:
        # create a csv writer object
        csv_writer = csv.writer(csvfile)
        # count the number of successfully processed articles
        successful = 0
        # for each article
        for article in articles:
            # get all relevant sentences
            sentences = [article.title, article.description, article.maintext]
            # process for classification i.e. for each ner_type get 16 tokens before and 16 after
            try:
                for phrase in proc.prepare_for_classification(ner_type, sentences):
                    # write that to a csv
                    csv_writer.writerow(phrase)
                successful += 1
            except RuntimeError as e:
                print(e)
                print(f'Failure in : {article.url_id}, skipping')
        return successful


def main():
    load_articles(get_links())


if __name__ == '__main__':
    output_file = PROCESSED_DATA_DIR / 'cardinal_classification.csv'
    all_articles = get_url_attributes()
    successful = retrieve_named_entities(output_file, all_articles)
    print(f'successfully retrived classification clauses from {successful} artilces out of {len(all_articles)}')
