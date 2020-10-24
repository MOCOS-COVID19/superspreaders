from googlesearch import search
from newspaper import Article
from newspaper.article import ArticleException
from pathlib import Path
from newsplease import NewsPlease, NewsArticle
import logging
from typing import List


def search_for_events(query: str = "ognisko koronawirusa", start: int = 0, stop: int = 50, num: int = 10):
    links = []
    for link in search(query, lang="pl", num=num, start=start, stop=stop):
        links.append(link)
    return links


def save_links(links: List[str]):
    links_file_path = Path('.').resolve().parent / 'data' / 'links.csv'
    with links_file_path.open('a') as output_file:
        output_file.write('\n'.join(links) + '\n')


def describe_article(article: NewsArticle) -> None:
    print('Authors', article.authors)
    print('Date download', article.date_download)
    print('Date modify', article.date_modify)
    print('Date publish', article.date_publish)
    print('Description', article.description)
    print('File name', article.filename)
    print('Image URL', article.image_url)
    print('Language', article.language)
    print('Local path', article.localpath)
    print('Title', article.title)
    print('Title page', article.title_page)
    print('Title RSS', article.title_rss)
    print('Source domain', article.source_domain)
    print('Main text', article.maintext)
    print('URL', article.url)


def fetch_with_newspaper(link: str) -> Article:
    article = Article(link)
    article.download()
    try:
        article.parse()
    except ArticleException:
        logging.warning('Article was not downloaded')
    return article


def fetch_with_newsplease(link: str) -> NewsArticle:
    return NewsPlease.from_url(link)


if __name__ == '__main__':
    start = 50
    stop = start + 50
    found_links = search_for_events(start=start, stop=stop)
    save_links(found_links)
