from typing import Optional, List
from datetime import datetime
import json

import boto3
from sqlalchemy import create_engine, inspect
from sqlalchemy import Select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import functions
from sqlalchemy_utils import database_exists, create_database


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=functions.now())
    published_time: Mapped[datetime]
    author: Mapped[str]
    headline: Mapped[str]
    subheading: Mapped[str]
    content: Mapped[str]
    translated_headline: Mapped[Optional[str]] = mapped_column(default=None)
    translated_subheading: Mapped[Optional[str]] = mapped_column(default=None)
    translated_content: Mapped[Optional[str]] = mapped_column(default=None)
    summary: Mapped[Optional[str]] = mapped_column(default=None)
    article_url: Mapped[str]
    image_url: Mapped[str]
    image_filename: Mapped[str]
    s3_url: Mapped[Optional[str]] = mapped_column(default=None)


class Database:
    def __init__(self, local: bool = True) -> None:
        if local:
            self._engine = create_engine("sqlite:///./../sqlite3.db", echo=False)
        else:
            self._engine = create_engine(get_db_uri(), echo=False)

        if not database_exists(self._engine.url):
            create_database(self._engine.url)

        insp = inspect(self._engine)
        if not insp.has_table(Article.__tablename__):
            Base.metadata.create_all(self._engine)

        self._session_maker = sessionmaker(bind=self._engine)

    def add_to_db(self, article: Article) -> None:
        with self._session_maker() as session:
            session.add(article)
            session.commit()

    def get_articles(self, offset=None, limit=None) -> List[Article] | None:
        with self._session_maker() as session:
            articles = (
                session.query(Article)
                .order_by(Article.published_time.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return articles

    def get_num_articles(self) -> int:
        with self._session_maker() as session:
            return session.query(Article).count()

    def article_exists(self, article_url: str) -> bool:
        with self._session_maker() as session:
            statement = Select(Article).where(Article.article_url == article_url)
            if session.execute(statement).one_or_none():
                return True
            return False

    def get_null_summary_articles(self) -> List[Article] | None:
        with self._session_maker() as session:
            articles = session.query(Article).where(Article.summary == None)
            return articles

    def add_translations(
        self, id: int, headline: str, subheading: str, content: str
    ) -> None:
        with self._session_maker() as session:
            article = session.get(Article, id)
            article.translated_headline = headline
            article.translated_subheading = subheading
            article.translated_content = content
            session.commit()
            session.flush()

    def add_summary(self, id: int, summary: str) -> None:
        with self._session_maker() as session:
            article = session.get(Article, id)
            article.summary = summary
            session.commit()
            session.flush()


def get_db_uri() -> str:
    session = boto3.Session()
    client = session.client("secretsmanager", region_name="eu-west-1")
    secret_string = client.get_secret_value(
        SecretId="eve-project-a9562e1a1783b0e4"
    ).get("SecretString")
    secret = json.loads(secret_string)
    return secret["db_uri"]
