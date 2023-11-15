FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.in .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.in

RUN mkdir /app/src

COPY src /app/src

RUN mkdir /app/db

COPY  db /app/db

EXPOSE 8000

CMD [ "python", "src/main.py" ]