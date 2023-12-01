import math

import streamlit as st
import database

st.set_page_config(page_title="Valor Econômico Summarizer", page_icon="📝")

st.title("📝 Valor Econômico Summarizer")

paginate = st.checkbox("Paginate")


@st.cache_resource
def get_db():
    db = database.Database(local=False)
    return db


def get_num_articles():
    db = get_db()
    return db.get_num_articles()


def get_articles(limit: int | None = None, offset: int | None = None):
    db = get_db()
    return db.get_articles(limit=limit, offset=offset)


if paginate:
    limit = 5
    choices = (i for i in range(1, math.ceil(get_num_articles() / limit) + 1))
    page = st.selectbox("Page Number", choices)
    offset = (page - 1) * limit
    articles = get_articles(limit=limit, offset=offset)
else:
    limit = None
    offset = None
    articles = get_articles(limit=limit, offset=offset)


for article in articles:
    st.header(article.translated_headline)
    st.image(article.image_url)
    st.subheader(article.translated_subheading)
    st.caption(
        f'{article.author} - {article.published_time.strftime("%d/%m/%Y %H:%M")}'
    )
    st.write(f"[Source]({article.article_url})")
    with st.expander("See Summary"):
        st.write(article.translated_content.replace("$", "\$").replace(". ", ".\n\n"))
    st.divider()
