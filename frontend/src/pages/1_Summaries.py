import streamlit as st
import database

st.set_page_config(page_title="Valor Econômico Summarizer", page_icon="📝")

st.title("📝 Valor Econômico Summarizer")


@st.cache_resource
def get_articles():
    db = database.Database()
    articles = db.get_articles()
    return articles


articles = get_articles()

for article in articles:
    st.header(article.translated_headline)
    st.image(article.image_url)
    st.subheader(article.translated_subheading)
    st.caption(f'{article.author} - {article.published_time.strftime("%m/%d/%Y")}')
    st.write(f"[Source]({article.article_url})")
    with st.expander("See Summary"):
        st.write(article.translated_content.replace("$", "\$").replace(". ", ".\n\n"))
    st.divider()
