import logging
import string
from datetime import datetime
from pathlib import Path
from typing import List, Union

import xlsxwriter.format
from newspaper.article import ArticleDownloadState
from tqdm import tqdm

from src import constants as const
from src.data.database import get_session, get_url_attributes
from src.data.entities import URLAttributes, URL
from src.ner import processor
from src.webscrapping.downloader import fetch_with_newspaper

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def load_new_articles() -> None:
    with get_session() as session:
        links = session.query(URL).filter(URL.article == None)
        logging.info(f'Found {links.count()} URLs without matching articles')
        unresolvable = []
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
            elif article.download_state == ArticleDownloadState.FAILED_RESPONSE:
                unresolvable.append(link)
        # remove those links that we are unable to download articles for
        for link in unresolvable:
            session.delete(link)
        session.commit()


class ClassificationTrainsetBuilder:
    MARKING_FORMAT = {'color': 'red'}
    HEADER_FORMAT = {'bold': True, 'align': 'center', 'valign': 'middle', 'border': 1}

    @staticmethod
    def generate_rich_string(tokens: List[str], should_format: List[bool],
                             xlsx_format: xlsxwriter.format.Format) -> List[Union[str, xlsxwriter.format.Format]]:
        """
        Generate rich string used for formatted output in excel files.

        :param tokens: list of token textx
        :param should_format list of boolean flags whether to format a given word
        :param xlsx_format: format class defining the formatting
        :return: list of string mixed with format object before pieces that should be formatted.
        """
        rich_string = []
        for token, is_formatted in zip(tokens, should_format):
            if token is None:
                continue
            if is_formatted:
                rich_string.extend([xlsx_format, ' ' + token])
            else:
                rich_string.append(' ' + token if token not in string.punctuation else token)

        return rich_string

    @staticmethod
    def _get_formatting_mask(length: int, offset: int = 16) -> List[bool]:
        return ([False] * offset) + ([True] * (length - 2 * offset)) + ([False] * offset)

    @classmethod
    def retrieve_named_entities_to_excel(cls, output_file: Path, articles: List[URLAttributes],
                                         ner_type: str = const.NER.CARDINAL) -> int:
        # article processor
        proc = processor.ArticleProcessor.get_instance()

        # count the number of successfully processed articles
        successful = 0

        # list of problematic articles that need to be handled
        problematic_articles = [5, 27]

        # output excel file
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet()
        # headers
        header_format = workbook.add_format(cls.HEADER_FORMAT)
        for i, header in enumerate(['url_id', 'text', 'class']):
            worksheet.write(0, i, header, header_format)

        # prepare the flags for formatting
        offset = 16
        marking_format = workbook.add_format(cls.MARKING_FORMAT)

        row = 1
        try:

            # for each article
            for article in tqdm(articles):
                if article.url_id in problematic_articles:
                    continue
                # get all relevant sentences
                sentences = [article.title, article.description, article.maintext]
                # process for classification i.e. for each ner_type get 16 tokens before and 16 after
                try:
                    for i, phrase in enumerate(proc.prepare_for_classification(ner_type, sentences, offset), 1):
                        # write the phrase to the excel file
                        formatting = cls._get_formatting_mask(len(phrase), offset)
                        rich_string = cls.generate_rich_string(phrase, formatting, marking_format)
                        if len(rich_string) > 0:
                            worksheet.write(row, 0, article.url_id)
                            worksheet.write_rich_string(row, 1, *rich_string)
                            row += 1

                    successful += 1
                except RuntimeError:
                    logging.exception(f'Failure in : {article.url_id}, skipping')
        finally:
            workbook.close()
        return successful


def main():
    load_new_articles()
    # output_file = const.Classification.CARDINAL_PATH
    id = 6
    output_file = const.PROCESSED_DATA_DIR / f'article_{id}.xlsx'
    all_articles = get_url_attributes(id)
    successful = ClassificationTrainsetBuilder().retrieve_named_entities_to_excel(output_file, all_articles)
    print(f'successfully retrieved classification clauses from {successful} articles out of {len(all_articles)}')


if __name__ == '__main__':
    main()
