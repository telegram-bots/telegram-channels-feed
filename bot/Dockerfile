FROM python:3.6.1-slim
RUN mkdir -p /code/data
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
CMD ["python", "-u", "run.py"]
