FROM python:3.6.2-alpine3.6
RUN mkdir /code/
RUN mkdir -p /data/files/
WORKDIR /code
ADD requirements.txt /code/
RUN apk add --no-cache libpq gcc postgresql-dev musl-dev && pip install -r requirements.txt && apk del gcc postgresql-dev musl-dev
ADD . /code/
CMD ["python", "-u", "run.py"]
