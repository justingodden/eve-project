FROM python:3.11-slim-bookworm

WORKDIR /app

RUN mkdir /app/db

COPY  db /app/db

COPY requirements.in .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.in

RUN mkdir /app/src

COPY src /app/src

EXPOSE 8000

CMD [ "python", "src/main.py" ]