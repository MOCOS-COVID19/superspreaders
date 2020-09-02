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
    article = NewsPlease.from_url(link)
    print(article.title)
    print(article.maintext)


if __name__ == '__main__':
    start = 50
    stop = start + 50
    found_links = search_for_events(start=start, stop=stop)
    save_links(found_links)