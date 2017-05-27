FROM python:3.6.1-slim
RUN mkdir /code/
RUN mkdir -p /data/files/
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
CMD ["python", "-u", "run.py"]
