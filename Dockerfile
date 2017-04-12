FROM python:3.6.1-slim
ENV DATABASE_URL "host=db dbname=postgres user=postgres"
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
