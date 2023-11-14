FROM python:3.10

WORKDIR /app

COPY requirements.in .
RUN pip install --no-cache-dir -r requirements.in

RUN mkdir /app/src

COPY src /app/src

CMD [ "python", "src/main.py" ]