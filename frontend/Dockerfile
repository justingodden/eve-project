FROM python:3.10-slim-bookworm

WORKDIR /app

COPY requirements.in .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.in

RUN mkdir /app/src

COPY src /app/src

RUN mkdir ~/.streamlit

COPY config.toml ~/.streamlit/config.toml

EXPOSE 8501

CMD [ "streamlit", "run", "src/Home.py" ]