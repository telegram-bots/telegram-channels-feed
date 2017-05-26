FROM python:3.6.1-slim
ENV FLASK_APP "/code/src/__init__.py"
RUN apt-get update -y && apt-get install -y --no-install-recommends libmagic-dev
RUN mkdir -p /code/data
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
EXPOSE 5000
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
