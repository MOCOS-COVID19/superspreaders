from googlesearch import search
from newsplease import NewsPlease
from pathlib import Path


def search_for_events(query = "ognisko koronawirusa", start=0, stop=50, num=10):
    links = []
    for link in search(query, lang="pl", num=num, start=start, stop=stop):
        links.append(link)
    return links


def save_links(links):
    links_file_path = Path('.').resolve().parent / 'data' / 'links.csv'
    with links_file_path.open('a') as output_file:
        output_file.write('\n'.join(links) + '\n')


def fetch(link):
    return NewsPlease.from_url(link)


def describe_article(article):
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


if __name__ == '__main__':
    start = 50
    stop = start + 50
    found_links = search_for_events(start=start, stop=stop)
    save_links(found_links)