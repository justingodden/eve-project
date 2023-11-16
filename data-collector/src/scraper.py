from typing import List
from dataclasses import dataclass

from urllib3.response import HTTPResponse
import requests
from bs4 import BeautifulSoup

from database import Article


@dataclass
class ScrapedArticle:
    headline: str
    subheading: str
    author: str
    published_time: str
    content: str
    article_url: str
    image_url: str


class Scraper:
    def __init__(self):
        self.ARTICLES_PAGE_URL = "https://valor.globo.com/financas/"
        self.HEADLINE_DIV_CLASSNAME = "highlight"
        self.ARTICLE_LIST_CLASSNAME = "bastian-feed-item"
        self.HEADLINE_CLASSNAME = "content-head__title"
        self.SUBHEADING_CLASSNAME = "content-head__subtitle"
        self.AUTHOR_ITEMPROP = "name"
        self.PUBLISHED_TIME_ITEMPROP = "datePublished"
        self.PARAGRAPH_CLASSNAME = "content-text__container"
        self.IMG_CLASSNAME = "content-media__image"

        self.article_urls = []
        self.img_urls = []

    @staticmethod
    def get_html(url: str) -> BeautifulSoup:
        r = requests.get(url)
        return BeautifulSoup(r.content, "html.parser")

    def get_headline(self, soup: BeautifulSoup) -> str:
        return soup.find("h1", {"class": self.HEADLINE_CLASSNAME}).text

    def get_subheading(self, soup: BeautifulSoup) -> str:
        return soup.find("h2", {"class": self.SUBHEADING_CLASSNAME}).text

    def get_author(self, soup: BeautifulSoup) -> str | None:
        author = soup.find("meta", {"itemprop": self.AUTHOR_ITEMPROP})
        if author:
            return author["content"]
        return author

    def get_published_time(self, soup: BeautifulSoup) -> str:
        return soup.find("time", {"itemprop": self.PUBLISHED_TIME_ITEMPROP})["datetime"]

    def get_content(self, soup: BeautifulSoup) -> List[str]:
        return [p.text for p in soup.find_all("p", {"class": self.PARAGRAPH_CLASSNAME})]

    def get_img_url(self, soup: BeautifulSoup) -> List[str]:
        try:
            return soup.find("img", {"class": self.IMG_CLASSNAME})["src"]
        except:
            return soup.find("img", {"class": "content-featured-image"})["src"]

    def get_headline_article_urls(self, soup: BeautifulSoup) -> List[str]:
        return [
            soup.find("div", {"class": self.HEADLINE_DIV_CLASSNAME}).find("a")["href"]
        ]

    def get_article_list_urls(self, soup: BeautifulSoup) -> List[str]:
        return [
            div.find("a")["href"]
            for div in soup.find("div", {"id": "bstn-launcher"}).find_all(
                "div", {"class": self.ARTICLE_LIST_CLASSNAME}
            )
        ]

    def get_urls(self) -> List[str]:
        soup = self.get_html(self.ARTICLES_PAGE_URL)
        self.article_urls += self.get_headline_article_urls(soup)
        self.article_urls += self.get_article_list_urls(soup)
        return self.article_urls

    def scrape_article(self, url) -> Article:
        soup = self.get_html(url)
        article = ScrapedArticle(
            headline=self.get_headline(soup),
            subheading=self.get_subheading(soup),
            author=self.get_author(soup),
            published_time=self.get_published_time(soup),
            content=self.get_content(soup),
            image_url=self.get_img_url(soup),
            article_url=url,
        )
        return article

    @staticmethod
    def get_image_data(image_url: str) -> HTTPResponse | None:
        r_img = requests.get(image_url, stream=True)
        if r_img.status_code == 200:
            return r_img.raw
        else:
            return None
