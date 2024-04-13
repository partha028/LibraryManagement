FROM python:3.11.5

ENV PYHONUNBUFFERED 1

WORKDIR /app

ADD . /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN pip install pymongo

COPY . /app  



