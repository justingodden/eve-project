import llm
import database


def main() -> None:
    db = database.Database()
    articles = db.get_null_summary_articles()
    count = articles.count()

    for i, article in enumerate(articles):
        translated_headline = llm.translate(article.headline)
        translated_subheading = llm.translate(article.subheading)
        translated_content = llm.translate(article.content)
        db.add_translations(
            article.id, translated_headline, translated_subheading, translated_content
        )
        summary = llm.summarize(
            f"{translated_headline}\n{translated_subheading}\n\n{translated_content}"
        )
        db.add_summary(article.id, summary)
        print(f"{i+1}/{count} articles summarized...", end="\r")


if __name__ == "__main__":
    main()
