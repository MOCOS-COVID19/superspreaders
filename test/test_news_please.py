from unittest import TestCase
from webscrapping import downloader


class TestNewsPlease(TestCase):
    def test_read_one_text(self):
        url = r'https://tvn24.pl/pomorze/koronawirus-w-polsce-gornicy-z-czerwonej-strefy-pojechali-nad-morze-nowe-ognisko-koronawirusa-4670186'
        article = downloader.fetch(url)
        print(article.title)
        print(article.maintext)