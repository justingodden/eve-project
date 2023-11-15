import llm
import database


def main() -> None:
    db = database.Database(local=False)
    articles = db.get_null_summary_articles()
    count = articles.count()

    for i, article in enumerate(articles):
        print(f"Article {i+1}/{count}: Translating Headline...")
        translated_headline = llm.translate(article.headline)
        print(f"Article {i+1}/{count}: Translating Subheading...")
        translated_subheading = llm.translate(article.subheading)
        print(f"Article {i+1}/{count}: Translating Content...")
        translated_content = llm.translate(article.content)
        db.add_translations(
            article.id, translated_headline, translated_subheading, translated_content
        )
        print(f"Article {i+1}/{count}: Summarizing...")
        summary = llm.summarize(
            f"{translated_headline}\n{translated_subheading}\n\n{translated_content}"
        )
        db.add_summary(article.id, summary)


if __name__ == "__main__":
    main()
