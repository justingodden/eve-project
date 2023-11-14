from scraper import Scraper
from cleaner import Cleaner
from database import Database, Article
from uploader import Uploader


def main() -> None:
    scraper = Scraper()
    cleaner = Cleaner()
    db = Database()
    uploader = Uploader()

    article_urls = scraper.get_urls()

    for i, url in enumerate(article_urls):
        try:
            if not db.article_exists(url):
                article = Article()
                scraped_article = scraper.scrape_article(url)
                article.headline = scraped_article.headline
                article.subheading = scraped_article.subheading
                article.author = scraped_article.author
                article.published_time = cleaner.clean_published_time(
                    scraped_article.published_time
                )
                article.content = cleaner.clean_content(scraped_article.content)
                article.article_url = url
                article.image_url = scraped_article.image_url
                article.image_filename = cleaner.extract_image_filename(
                    scraped_article.image_url
                )

                image_data = scraper.get_image_data(scraped_article.image_url)
                uploader.save_image(image_data, article.image_filename)

                db.add_to_db(article)
            print(f"{i+1}/{len(article_urls)} articles scraped...", end="\r")

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
