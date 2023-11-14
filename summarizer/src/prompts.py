translate_template = """Translate the following text from Portuguese to English.

PORTUGUESE: {text}

ENGLISH:"""

summary_template = """You are an analyst working for an investment bank. Your job is to summarize news articles to be more easily digested by your manager. The article below is from an online economics newspaper. Summarize the article to present to your manager. Start with a bullet-point list that contains the key takeaways. Be sure to extract any key facts and figures or numbers. Then return a short paragraph summary. Be sure to consider good sentence structure, using line breaks where necessary to make it readable as an online article. It is very important that you begin with bullet-points and end with a single summary paragraph.

ARTICLE: {text}

BULLET-POINTS AND SUMMARY:"""
