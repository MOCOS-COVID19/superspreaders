from unittest import TestCase
from webscrapping import downloader


class TestNewsPlease(TestCase):
    def test_read_one_text(self):
        url = r'https://tvn24.pl/pomorze/koronawirus-w-polsce-gornicy-z-czerwonej-strefy-pojechali-nad-morze-nowe-ognisko-koronawirusa-4670186'
        article = downloader.fetch(url)
        print(article.title)
        print(article.maintext)

    def test2(self):
        # Gazeta wyborcza required subscription and blocks its content for webcrawling
        url = r'https://wroclaw.wyborcza.pl/wroclaw/7,35771,26231183,ognisko-koronawirusa-na-pogotowiu-jest-wiecej-zakazonych.html'
        article = downloader.fetch(url)
        downloader.describe_article(article)

    def test3(self):
        url = r'https://radio.lublin.pl/2020/08/4-nowe-ogniska-koronawirusa-wojewodztwie-lubelskim/'
        article = downloader.fetch(url)
        downloader.describe_article(article)

    def test4(self):
        url = r'https://m.sadeczanin.info/wiadomosci/nowy-sacz-ognisko-koronawirusa-w-dps-sa-juz-wyniki-badan'
        article = downloader.fetch(url)
        downloader.describe_article(article)