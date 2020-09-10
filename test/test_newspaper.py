from unittest import TestCase
from newspaper import Article
from src.webscrapping import downloader

class TestNewspaper3k(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = r'https://m.sadeczanin.info/wiadomosci/nowy-sacz-ognisko-koronawirusa-w-dps-sa-juz-wyniki-badan'
        cls.article = Article(cls.url, lang='pl')
        cls.article.download()

    def test_after_download(self):
        assert self.article.html.startswith('<!DOCTYPE html>')

        self.article.parse()
        assert str(self.article.publish_date) == '2020-08-22 16:07:50+02:00'
        print('title')
        print(self.article.title)
        assert self.article.title == 'Nowy Sącz: ognisko koronawirusa w DPS. Są już wyniki badań'
        print('\nmeta description')
        print(self.article.meta_description)

        print('\ntext')
        print(self.article.text)

        # The code gives some results of NLP on the article, but it does not seem useful for the project. Code
        # snippets with respective outputs are given below for presentation purposes.
        # self.article.nlp()

        # print(self.article.keywords)
        # ['osoby', 'są', 'ognisko', 'już', 'że', 'osób', 'wyniki', 'sącz', 'nowy', 'z', 'wczoraj', 'koronawirusa', 'się', 'dps', 'mieszkańców', 'zostały', 'badań', 'w', 'od']

        # print(self.article.summary)
        # Prezydent miasta Ludomir Handzel informował wczoraj o tym, że znane są wyniki 90 z 275 osób, od których w środę zostały pobrane wymazy w kierunku SARS-CoV-2.
        # Gospodarz miasta informował mieszkańców również o tym, że w związku z pojawieniem się ogniska koronawirusa wszystko odbywa się zgodnie z procedurami, aby zapanować nad ogniskiem i uniemożliwić dalsze rozprzestrzenianie się zakażenia.
        # Prezydent Handzel zapewnił wczoraj mieszkańców, że od 12 marca pensjonariusze nie opuszczali Domu Pomocy Społecznej.
        # - Liczba osób z potwierdzonym wynikiem to szesnastu pracowników DPS i siedemdziesięcioro mieszkańców – powiedziała portalowi Sądeczanin.info, Luiza Piątkiewicz, dyrektor Miejskiego Ośrodka Pomocy Społecznej w Nowym Sączu.
        # - Zakażeni mieszkańcy zostali odizolowani od osób zdrowych i poddani izolacji w jednym z budynków, a część osób z pozytywnym wynikiem objętych jest izolacją domową.


class TestDownloader(TestCase):

    def test_fetch(self):
        url = r'https://zdrowie.wprost.pl/koronawirus/w-polsce/10351289/ogniska-koronawirusa-na-mazowszu-zaklady-pracy-dps-szpital-i-kilka-po-imprezach-rodzinnych.html'
        article = downloader.fetch(url)
        print(article.publish_date)
        print(article.title)
        print(article.meta_description)
        print(article.text)
